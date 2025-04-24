#!/usr/bin/env python3



"""
Scientific Discovery Crawler – clean JSON output (10k‑ready, recursive)

This script crawls Wikipedia for scientific discoveries. It crawls each seed
category and its sub‑categories (depth set in DEPTH_CRAWL), checks every page
with a language model, and saves true discoveries to a JSON file.

Dependencies
------------
    pip install requests openai beautifulsoup4
"""

import os, json, time, random, re, html, unicodedata
from typing import List, Dict, Tuple
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import requests
from bs4 import BeautifulSoup
import openai















# ---------------- SETTINGS ----------------
SAVE_LIMIT        = 10_000                       # stop after this many discoveries
DEPTH_CRAWL       = 3                            # category recursion depth
ARCHIVED_CATEGORIES  = [                            # root Wikipedia categories
    "Category:Scientific_discoveries",
    "Category:Chemistry_discoveries",
    "Category:Biological_discoveries",
    "Category:Physics_experiments",
    "Category:Chemical_compounds_discovered_in_the_20th_century",
    "Category:Chemical_compounds_discovered_in_the_19th_century",
    "Category:Inventions",
    "Category:Mathematical_theorems",
    "Category:First_syntheses_of_chemical_compounds",
]

START_CATEGORIES = [
    "Category:Scientific_theories",
    "Category:Technological_innovations",
    "Category:Engineering_innovations",
]
JSON_FILE         = "json files\discoveries.json"           # output data
CHECKPOINT_FILE   = r"json files\visited_links.json"         # store visited urls
STATS_FILE        = "json files\crawl_stats.json"           # post crawl stats
API_KEY = "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"
MODEL             = "gpt-4.1-mini"             
REQUEST_DELAY_SEC = 0.1                        # polite pause


def make_session() -> requests.Session:
    """Session with Wikipedia‑friendly headers and exponential‑back‑off retries."""
    s = requests.Session()
    s.headers.update(
        {
            "User-Agent": (
                "ScientificDiscoveryCrawler/1.0 "
                "(mailto:you@example.com)  "
                "bot politely fetching discovery pages"
            )
        }
    )
    retry = Retry(
        total=4,                # 1 original try + 4 retries  → 5 attempts max
        backoff_factor=0.75,    # 0.75, 1.5, 3.0, 6.0 s between retries
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
        raise_on_status=False,
        respect_retry_after_header=True,
    )
    adapter = HTTPAdapter(max_retries=retry)
    s.mount("https://", adapter)
    s.mount("http://", adapter)
    return s


SESSION = make_session()       # global, reused everywhere
JITTER_SEC = 0.05              # extra ± 50 ms on each polite pause

openai.api_key = API_KEY

# -------- PLAIN‑ENGLISH LLM PROMPT --------
PROMPT_TEMPLATE = """
You are vetting a Wikipedia page to decide if it really records a FIRST‑TIME
*scientific discovery or invention* that changed what scientists could DO or
UNDERSTAND.

Return EXACTLY three tokens, separated by dashes:
  is_discovery – year – is_person

──────────── What COUNTS ────────────
• Isolation / synthesis of a brand‑new substance
• Landmark experiment revealing a new physical or biological phenomenon
• First clear proof of a theory (experimentally or observationally)
• Invention of a tool or device **only if** it directly enabled new
  scientific results (e.g. X‑ray tube, electron microscope)

──────────── What does NOT count ────────────
• Named theorems, lemmas, or purely mathematical results
• Broad subjects, instruments, or techniques (e.g. “Physics”, “Microscope”)
• Generic devices that are mainly engineering or consumer tech
• Lists, timelines, glossaries, taxonomies
• Stretch of geologic time or group of organisms
• Biographies (if the page is mainly about a person)

──────────── Output rules ────────────
• is_discovery  : “true” or “false”
• year          : first 4‑digit year mentioned, or “unknown”
• is_person     : “true” if the page is a biography, else “false”
• Everything must be lowercase; no spaces.

──────────── Page excerpt ────────────
{intro}
──────────────────────────────────────
Examples
  Oxygen was first isolated in 1774 …      → true-1774-false
  DNA double helix model (1953) …          → true-1953-false
  The electron microscope (1931) …         → true-1931-false
  Photosynthesis is the process …          → false-unknown-false
  Dogs are a domestic species …            → false-unknown-false
  Marie Curie (born 1867) …                → false-unknown-true
"""

# -------------- VISITED LINKS --------------
visited: set[str] = set()
if os.path.exists(CHECKPOINT_FILE):
    try:
        with open(CHECKPOINT_FILE, "r", encoding="utf-8") as ck:
            visited = set(json.load(ck))
    except Exception:
        visited = set()

def save_visited_links() -> None:
    """Persist visited URL set."""
    with open(CHECKPOINT_FILE, "w", encoding="utf-8") as ck:
        json.dump(list(visited), ck, indent=2)

# ---------------- HELPERS ------------------

def make_ascii_safe(text: str) -> str:
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()


def shorten_description(raw: str, limit: int = 400) -> str:
    text = html.unescape(raw.replace("\n", " ")).strip()
    text = re.sub(r"\s+", " ", text)
    short = text[:limit]
    if "." in short:
        short = short.rsplit(".", 1)[0] + "."
    return short


def ask_gpt(prompt: str) -> str:
    try:
        resp = openai.ChatCompletion.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        return resp.choices[0].message.content.strip()
    except openai.error.RateLimitError:
        print(" OpenAI quota exceeded – pausing classification.")
        return "false-unknown-false"
    except Exception as exc:
        print("OpenAI error:", exc)
        return "false-unknown-false"""

# ----------- WIKIPEDIA HELPERS ------------

def get_category_items(cat: str, limit: int = 500) -> List[Tuple[str, int]]:
    """Return (title, namespace) for every item in a category, handling pagination."""
    url = "https://en.wikipedia.org/w/api.php"
    params = dict(action="query", list="categorymembers", cmtitle=cat,
                  cmlimit=limit, format="json")
    out: List[Tuple[str, int]] = []
    while True:
        data = requests.get(url, params=params, timeout=10).json()
        out.extend((m["title"], m["ns"]) for m in data["query"]["categorymembers"])
        if "continue" not in data:
            break
        params.update(data["continue"])  # follow pagination token
    return out


def crawl_category_tree(cat: str, depth: int = 3) -> List[str]:
    """Return all article URLs under `cat` up to `depth` levels deep."""
    print(f"  Crawling {cat}…", flush=True)
    seen_cats = {cat}
    pages: set[str] = set()
    stack = [(cat, 0)]
    while stack:
        current, d = stack.pop()
        for title, ns in get_category_items(current):
            if ns == 0:  # article
                pages.add("https://en.wikipedia.org/wiki/" + title.replace(" ", "_"))
            elif ns == 14 and d < depth:  # sub‑category
                sub = "Category:" + title.split("Category:", 1)[-1]
                if sub not in seen_cats:
                    seen_cats.add(sub)
                    stack.append((sub, d + 1))
    return list(pages)

def get_page_text(url: str) -> str:
    slug = url.split("/")[-1]
    endpoint = f"https://en.wikipedia.org/api/rest_v1/page/html/{slug}"

    try:
        resp = SESSION.get(endpoint, timeout=(5, 20))   # (connect, read) timeouts
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        # Any network hiccup – log and skip
        print(f"⏱️  Wikipedia fetch failed ({type(e).__name__}): {endpoint}")
        return ""

    soup = BeautifulSoup(resp.text, "html.parser")
    title = soup.find("h1").text if soup.find("h1") else slug.replace("_", " ")
    paras = " ".join(p.text for p in soup.find_all("p")[:3])
    rows  = soup.select("table.infobox tr")
    infobox = " ".join(r.get_text(' ', strip=True) for r in rows[:10])
    return make_ascii_safe(f"{title}\n{infobox}\n{paras}")


def classify_page(text: str):
    prompt = PROMPT_TEMPLATE.format(intro=text)
    raw = ask_gpt(prompt).lower().strip()
    parts = raw.split("-")
    if len(parts) != 3:
        return False, "unknown", False
    disc, yr, person = parts
    return disc.startswith("t"), (yr if yr.isdigit() else "unknown"), person.startswith("t")

# -------------------- MAIN ------------------

def main():
    next_id = 1
    saved_count = 0
    pages_checked = 0
    discoveries: List[Dict] = []
    url_queue: List[str] = []

    
    # Load existing discoveries if file exists
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            try:
                discoveries = json.load(f)
                if discoveries:
                    next_id = max(item["id"] for item in discoveries) + 1
            except Exception as e:
                print("Error loading JSON file:", e)
                discoveries = []
                next_id = 1

    print(f"Loaded {len(visited)} visited URLs")
    print(f"Loaded {len(discoveries)} saved discoveries\n", flush=True)


    print(f"\nBuilding queue from {len(START_CATEGORIES)} root categories (depth {DEPTH_CRAWL})…", flush=True)

    for cat in START_CATEGORIES:
        url_queue.extend(crawl_category_tree(cat, DEPTH_CRAWL))
    random.shuffle(url_queue)

    print(f"Queue ready: {len(url_queue)} pages. Target = {SAVE_LIMIT} discoveries.\n", flush=True)

    while url_queue and saved_count < SAVE_LIMIT:
        url = url_queue.pop()
        if url in visited:
            continue
        visited.add(url)
        save_visited_links()

        pages_checked += 1

        if pages_checked % 100 == 0:
            print(f"Progress: {pages_checked} pages checked, {saved_count} discoveries saved.", flush=True)


        title = url.split("/")[-1].replace("_", " ")
        if title.startswith("Category:") or title.startswith("List_of"):
            continue  # skip umbrella pages
        
        page_text = get_page_text(url)
        if not page_text or "\n" not in page_text:
            print(f"Skipping {title}: no usable text or bad format", flush=True)
            continue
        is_disc, year, is_person = classify_page(page_text)

        #Debug (caused crash when running for hours on VScode alter to 1 in 50/100 if needed to run the whole crawl)
        #print(f"Checked {title}: discovery={is_disc}, year={year}, person={is_person}")

        with open("log.txt", "a", encoding="utf-8") as log:
            log.write(f"{title}: is_disc={is_disc}, year={year}, person={is_person}\n")

        if is_disc and not is_person:
            
            person_indicators = [
                "born ", "died ",
            ]
            lower_text = page_text.lower()
            if any(phrase in lower_text for phrase in person_indicators):
                print(f"  Skipped likely biography: {title}", flush=True)
                continue
            
            if any(d["url"] == url for d in discoveries): #Checks for duplicate names in discoveries Json and skips
                print(f"  Skipping duplicate discovery already saved: {title}")
                continue

            desc = shorten_description(page_text.split("\n", 1)[1])
            discoveries.append({
                "id": next_id,
                "name": title,
                "year": year,
                "description": desc,
                "url": url,
            })
            next_id += 1
            saved_count += 1
            print(f"  Saved {saved_count}: {title} ({year})")

            if saved_count % 25 == 0:
                with open(JSON_FILE, "w", encoding="utf-8") as jf:
                    json.dump(discoveries, jf, indent=2)
                print(f"🗃️ Autosaved {saved_count} discoveries to {JSON_FILE}", flush=True)

        time.sleep(REQUEST_DELAY_SEC + random.uniform(-JITTER_SEC, JITTER_SEC))


    with open(JSON_FILE, "w", encoding="utf-8") as jf:
        json.dump(discoveries, jf, indent=2)

    with open(STATS_FILE, "w", encoding="utf-8") as sf:
        json.dump({"visited": pages_checked, "saved": saved_count}, sf, indent=2)

    print(f"\nDone! Visited {pages_checked} pages; saved {saved_count} discoveries.\n")

# Run the program
main()
