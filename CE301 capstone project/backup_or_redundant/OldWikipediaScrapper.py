import requests, openai, csv, os, json, time, unicodedata

# ---------------- CONSTANTS ----------------
DEPTH_LIMIT       = 3
LINK_SCRAP_LIMIT  = 20
START_URL         = "https://en.wikipedia.org/wiki/Enzyme"
API_KEY = "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"
MODEL             = "gpt-4.1-nano"
CSV_FILE          = "scientific_concepts.csv"
CHECKPOINT_FILE   = "visited_links.json"
REQUEST_DELAY_SEC = 0.5

PROMPT_TEMPLATE = """
You are an expert science historian.

A *discovery* for this project is any first‑time event that let scientists
*work with* or *reason about* something new:

• isolation or synthesis of a substance (oxygen 1774, carbon dioxide 1754)
• first clear experimental demonstration (gene expression 1961)
• invention of a pivotal technique or database (X‑ray crystal 1912, PDB 1971)
• publication that crystallised a new field (entropy 1865, thermodynamics 1824)

Below is the first paragraph of a Wikipedia article:

{intro}

Return exactly three tokens separated by dashes:  is_discovery-year-is_person

  is_discovery : "true"  or "false"
  year         : 4‑digit year of that first event, or "unknown"
  is_person    : "true"  if the whole page is a biography, else "false"

Examples  
  Oxygen was first isolated in 1774 → true-1774-false  
  Metabolism is a broad set of processes → false-unknown-false  
  Marie Curie (born 1867)…           → false-unknown-true
"""

openai.api_key = API_KEY

# -------------- VISITED CHECKPOINT -------------
visited = set()
if os.path.exists(CHECKPOINT_FILE):
    try:
        s = open(CHECKPOINT_FILE, "r", encoding="utf-8").read().strip()
        if s:
            visited = set(json.loads(s))
    except Exception:
        visited = set()

def save_checkpoint() -> None:
    with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
        json.dump(list(visited), f)

# -------------- ID INITIALISATION -------------
if os.path.exists(CSV_FILE) and os.path.getsize(CSV_FILE) > 0:
    with open(CSV_FILE, newline="", encoding="utf-8") as f:
        current_id = sum(1 for _ in csv.reader(f))        # header counts as 1
else:
    current_id = 1

# -------------- SMALL HELPERS -----------------
def ascii_safe(text: str) -> str:
    """Remove non‑ASCII so headers never fail."""
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()

def query_LLM(prompt: str) -> str:
    try:
        resp = openai.ChatCompletion.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are concise and precise."},
                {"role": "user",   "content": prompt}
            ],
            temperature=0
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        print("⚠️ OpenAI error:", e)
        return ""

def fetch_intro_text(url: str) -> str:
    title = url.split("/")[-1]
    api   = f"https://en.wikipedia.org/api/rest_v1/page/summary/{title}"
    try:
        r = requests.get(api, timeout=10)
        if r.status_code == 200:
            return r.json().get("extract", "").strip()
    except Exception:
        pass
    return ""

def classify_intro(intro: str):
    clean_intro = ascii_safe(intro)
    prompt      = PROMPT_TEMPLATE.format(intro=clean_intro)
    raw         = query_LLM(prompt).lower().strip()
    parts       = raw.split('-')
    if len(parts) != 3:
        return False, "unknown", False
    disc, yr, person = parts
    return disc.startswith('t'), (yr if yr.isdigit() else "unknown"), person.startswith('t')

def get_description_from_api(url: str) -> str:
    title = url.split('/')[-1]
    api   = f"https://en.wikipedia.org/api/rest_v1/page/summary/{title}"
    try:
        r = requests.get(api, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if data.get("extract"):
                return data["extract"].strip()
    except Exception:
        pass
    return "Description unavailable."

def scrape_wikipedia_links(url: str, limit: int):
    try:
        html = requests.get(url, timeout=10).text
        out  = []
        for h in html.split('href="/wiki/')[1:]:
            slug = h.split('"', 1)[0]
            if ':' not in slug:
                full = "https://en.wikipedia.org/wiki/" + slug
                if full not in visited and full not in out:
                    out.append(full)
            if len(out) >= limit:
                break
        return out
    except Exception:
        return []

def is_bad_page(title: str):
    return any(prefix in title for prefix in (
        "Main_Page", "Index_of_", "List_of_", "Outline_of_"
    ))

# -------------- MAIN CRAWLER ------------------
def explore_discoveries(url: str, depth: int, writer):
    global current_id
    if depth > DEPTH_LIMIT or url in visited:
        return
    visited.add(url); save_checkpoint()

    children = scrape_wikipedia_links(url, LINK_SCRAP_LIMIT)
    print(f"\n→ Depth {depth} — {len(children)} links")

    for link in children:
        name  = link.split('/')[-1].replace('_', ' ')
        intro = fetch_intro_text(link)

        if not intro or is_bad_page(name):
            continue

        is_disc, year, is_person = classify_intro(intro)
        print(f"Checked {name}: discovery={is_disc}, year={year}, person={is_person}")

        if is_disc and not is_person:
            desc = get_description_from_api(link)
            writer.writerow([current_id, name, year, desc, link])
            print(f"[Saved] {current_id}: {name} ({year})")
            current_id += 1

        # Always recurse so we can find discoveries deeper down
        explore_discoveries(link, depth + 1, writer)

        visited.add(link); save_checkpoint()
        time.sleep(REQUEST_DELAY_SEC)


# -------------- ENTRY -------------------------
def main():
    global current_id
    mode = 'a' if os.path.exists(CSV_FILE) else 'w'
    with open(CSV_FILE, mode, newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if mode == 'w':
            writer.writerow(["ID", "Name", "Discovery Date", "Description", "URL"])
        print("Starting from:", START_URL)
        explore_discoveries(START_URL, 1, writer)
    print("\nDone! Total discoveries saved:", current_id - 1)

if __name__ == "__main__":
    main()
