import json
import random

chunks = json.load(open("chunks.json", encoding="utf-8"))

# Print 5 random chunks
sample = random.sample(chunks, 5)
for i, c in enumerate(sample, 1):
    source = c["source"].split("/")[-1]
    print(f"--- Chunk {i} ({source}) ---")
    print(c["text"])
    print()

# Print full cleaned text of one document
print("\n========== FULL DOCUMENT: Biomes ==========")
biome_chunks = [c for c in chunks if "Biomes" in c["source"]]
full_text = " ".join(c["text"] for c in biome_chunks)
print(full_text[:3000])  # first 3000 chars is enough to spot any artifacts
