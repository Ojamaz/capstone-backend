import json

VISITED_FILE = "visited_links.json"
LAST_GOOD_URL = "https://en.wikipedia.org/wiki/Dujiangyan"

def main():
    with open(VISITED_FILE, "r", encoding="utf-8") as f:
        links = json.load(f)

    if LAST_GOOD_URL not in links:
        print("Could not find last good URL in visited list.")
        return

    cutoff_index = links.index(LAST_GOOD_URL) + 1
    print(f"Found GOOD URL at position {cutoff_index - 1} (keeping first {cutoff_index} links).")

    # Trim and save
    links = links[:cutoff_index]
    with open(VISITED_FILE, "w", encoding="utf-8") as f:
        json.dump(links, f, indent=2)

    print(f"fixed {VISITED_FILE} — now contains {len(links)} links.")

if __name__ == "__main__":
    main()
