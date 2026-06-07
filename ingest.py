import re
import json
import time
import requests
from bs4 import BeautifulSoup

SOURCES = [
    {"name": "Bosses",                "url": "https://terraria.wiki.gg/wiki/Bosses"},
    {"name": "Guide:Getting_started", "url": "https://terraria.wiki.gg/wiki/Guide:Getting_started"},
    {"name": "Hardmode",               "url": "https://terraria.wiki.gg/wiki/Hardmode"},
    {"name": "Guide:Class_setups",    "url": "https://terraria.wiki.gg/wiki/Guide:Class_setups"},
    {"name": "Biomes",                "url": "https://terraria.wiki.gg/wiki/Biomes"},
    {"name": "Events",                "url": "https://terraria.wiki.gg/wiki/Events"},
    {"name": "Movement_Accessories",  "url": "https://terraria.wiki.gg/wiki/Movement_Accessories"},
    {"name": "Combat_Accessories",    "url": "https://terraria.wiki.gg/wiki/Combat_Accessories"},
    {"name": "NPCs",                  "url": "https://terraria.wiki.gg/wiki/NPCs"},
    {"name": "Steam:World_Seeds",     "file": "documents/steam_seeds.txt", "url": "https://steamcommunity.com/sharedfiles/filedetails/?id=1283674938"},
]

CHUNK_SIZE = 500
OVERLAP = 50
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


def fetch_text(url):
    r = requests.get(url, headers=HEADERS, timeout=15)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    # Wiki pages use #mw-content-text; Steam guide pages use .guide_text
    content = (
        soup.find(id="mw-content-text")
        or soup.find(class_="guide_text")
        or soup.body
    )

    # Strip edit links, table of contents, navboxes, and wiki notice banners
    for unwanted in content.find_all(class_=["mw-editsection", "navbox", "toc", "messagebox", "hatnote"]):
        unwanted.decompose()
    for unwanted in content.find_all(id="toc"):
        unwanted.decompose()

    text = content.get_text(separator=" ", strip=True)
    text = re.sub(r"\s+", " ", text).strip()

    # Remove known wiki boilerplate sentences
    boilerplate = [
        r"This is the main page whose information applies to[^.]*\.",
        r"This is a Guide page[^.]*\.",
        r"This means the page will walk you through[^.]*\.",
        r"It has been suggested that this page[^.]*\.",
        r"\[\s*discuss\s*\] Reason:[^.]*\.",
        r"For the differences of this information on[^.]*\.",
        r"Main article:[^.]*\.",
        r"Status:\s*(Under|Subject to) revision[^)]*\)",
    ]
    for pattern in boilerplate:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE).strip()

    return text


def load_local_file(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    return re.sub(r"\s+", " ", text).strip()


def chunk_text(text, source_url):
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + CHUNK_SIZE, len(text))
        chunk = text[start:end].strip()
        if chunk:
            chunks.append({"text": chunk, "source": source_url})
        if end == len(text):
            break
        start += CHUNK_SIZE - OVERLAP
    return chunks


def main():
    all_chunks = []

    for source in SOURCES:
        print(f"Fetching {source['name']}...")
        try:
            if "file" in source:
                text = load_local_file(source["file"])
            else:
                text = fetch_text(source["url"])
            chunks = chunk_text(text, source["url"])
            all_chunks.extend(chunks)
            print(f"  {len(chunks)} chunks | first chunk: {chunks[0]['text'][:80]!r}")
        except Exception as e:
            print(f"  FAILED: {e}")
        time.sleep(1)

    print(f"\nTotal chunks: {len(all_chunks)}")

    with open("chunks.json", "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)
    print("Saved to chunks.json")

    print("\n--- Verification ---")
    print(f"Chunk count: {len(all_chunks)}")
    print(f"Sample chunk sizes: {[len(c['text']) for c in all_chunks[:5]]}")
    print(f"Sources represented: {len({c['source'] for c in all_chunks})}/10")


if __name__ == "__main__":
    main()
