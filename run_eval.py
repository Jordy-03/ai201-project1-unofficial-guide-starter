from query import ask

questions = [
    "What item is used to manually summon the Eye of Cthulhu?",
    "What armor should a summoner player use in early Hardmode?",
    "What biome do you need to find Chlorophyte Ore, and what can mine it?",
    "What triggers a Blood Moon and what enemies does it spawn?",
    "What accessories improve movement speed in early game?",
]

for i, q in enumerate(questions, 1):
    print(f"\n{'='*70}")
    print(f"Q{i}: {q}")
    print("-" * 70)
    result = ask(q)
    print(f"Answer: {result['answer']}")
    print(f"Sources: {', '.join(result['sources'])}")
