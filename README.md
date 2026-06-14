# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

<!-- What topic or category of knowledge does your system cover?
     Why is this knowledge valuable, and why is it hard to find through official channels?
     Example: "Student reviews of CS professors at [university] — useful because official
     course descriptions don't reflect teaching style, exam difficulty, or workload." -->

The topic covers Terraria, a 2D adventure game where players progress by defeating various
bosses until they reach the "endgame". The AI agent is provided a database full of information
ranging from the best gear in post-hardmode to which is the first boss to defeat. The reason
why this information is valuable is because new players notoriously feel overwhelmed with
the amount of information to learn. Although there are dedicated wikipedia pages, looking
through the website requires having prior knowledge or already knowing what to look up. The
AI agent clarifies some of the confusion by providing suggestions.
---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | Terraria Wiki | Web page | https://terraria.wiki.gg/wiki/Bosses |
| 2 | Terraria Wiki | Web page | https://terraria.wiki.gg/wiki/Guide:Getting_started |
| 3 | Terraria Wiki | Web page | https://terraria.wiki.gg/wiki/Hardmode |
| 4 | Terraria Wiki | Web page | https://terraria.wiki.gg/wiki/Guide:Class_setups |
| 5 | Terraria Wiki | Web page | https://terraria.wiki.gg/wiki/Biomes |
| 6 | Terraria Wiki | Web page | https://terraria.wiki.gg/wiki/Events |
| 7 | Terraria Wiki | Web page | https://terraria.wiki.gg/wiki/Movement_Accessories |
| 8 | Terraria Wiki | Web page | https://terraria.wiki.gg/wiki/Combat_Accessories |
| 9 | Terraria Wiki | Web page | https://terraria.wiki.gg/wiki/NPCs |
| 10 | Steam Community | Local file | documents/steam_seeds.txt |

---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:**
500 characters

**Overlap:**
50 characters

**Why these choices fit your documents:**
Terraria wiki pages are structured reference content where useful information spans multiple sentences. A boss entry includes its name, spawn condition, and drops in close proximity, and splitting those apart would hurt retrieval. 500 characters keeps enough context together for the embedding to capture meaning without diluting it across too wide a window. Paragraph-based chunking was ruled out because wiki paragraphs vary wildly in length. 50-character overlap prevents key facts from being lost at chunk boundaries, which matters for pages like Guide:Class_setups where item names and their context sit near section edges.


**Final chunk count:** 929 chunks across 10 sources

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:**
all-MiniLM-L6-v2 (via sentence-transformers)


**Production tradeoff reflection:**
all-MiniLM-L6-v2 is fast and runs locally with no cost, but has a 256-token context limit — long wiki sections get truncated before embedding, which can weaken retrieval for dense pages. For a real deployment I'd weigh switching to OpenAI's text-embedding-3-small: better accuracy on domain-specific terminology (item names, biome names) and a much larger context window, at the cost of API latency and per-token pricing. Multilingual support isn't a concern here since all sources are English. For latency-sensitive production use, a locally hosted model like bge-large-en would be a middle ground — stronger than MiniLM without the network round-trip of an API call.

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:**

The system prompt explicitly forbids outside knowledge rather than just discouraging it:

> "You are a Terraria game guide assistant. Answer the user's question using ONLY the information in the provided context. Do not use any knowledge from outside the provided documents. If the context does not contain enough information to answer the question, respond with exactly: 'I don't have enough information in my documents to answer that.' Do not make up items, stats, or mechanics. Do not add information that is not present in the context."

Each retrieved chunk is labeled with its source in the context block (e.g., `[Source: Bosses]`) so the model can reference which document a fact came from.

**How source attribution is surfaced in the response:**

Source attribution is programmatic. After generation, unique source names are extracted directly from the ChromaDB metadata of the retrieved chunks and appended to the response. This guarantees attribution regardless of what the LLM outputs, rather than relying on the model to cite sources itself.

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | What item is used to manually summon the Eye of Cthulhu? | A Suspicious Looking Eye, crafted at a Demon or Crimson Altar using 6 Lens | "A Suspicious Looking Eye is used to manually summon the Eye of Cthulhu." | Relevant | Accurate |
| 2 | What armor should a summoner player use in early Hardmode? | Spider Armor, crafted from Spider Fangs dropped by Black Recluses in Spider Caves | "I don't have enough information in my documents to answer that." | Partially relevant | Inaccurate |
| 3 | What biome do you need to find Chlorophyte Ore, and what can mine it? | The Underground Jungle; requires a Pickaxe Axe or Drax, both crafted after defeating a Mechanical Boss | "Chlorophyte Ore can be found in the Underground Jungle. It can be mined with either the Drax or the Pickaxe Axe, or stronger." | Relevant | Accurate |
| 4 | What triggers a Blood Moon and what enemies does it spawn? | Occurs randomly at night (or by using a Bloody Tear); spawns Zombies, Demon Eyes, and Clowns | Correctly identified the 1/9 chance trigger and Bloody Tear, but noted the enemy list was not present in the retrieved context. | Partially relevant | Partially accurate |
| 5 | What accessories improve movement speed in early game? | Hermes Boots, Sailfish Boots, or Flurry Boots — combinable into Lightning Boots | Correctly identified the Aglet (+5% speed) but retrieved late-game items instead of Hermes Boots. | Partially relevant | Partially accurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:**
"What armor should a summoner player use in early Hardmode?"

**What the system returned:**
"I don't have enough information in my documents to answer that."

**Root cause (tied to a specific pipeline stage):**
The failure originates in the chunking stage. The Guide:Class_setups page organizes armor recommendations in HTML tables, with game stage (e.g., "Early Hardmode") as a row header and armor names as adjacent cells. When BeautifulSoup extracts table content with `get_text()`, the headers and data merge into a flat string like `"Great Helm Squire's Plating Tiki Pants Squire armor Hallowed armor..."` — the relationship between "early Hardmode" and "Spider Armor" is lost because they landed in different chunks. The embedding of a fragmented item list does not carry enough semantic signal for the model to confidently answer the question, so the LLM correctly refused rather than hallucinate.

**What you would change to fix it:**
Parse table rows explicitly during ingestion instead of using `get_text()` on the whole element. Each row (game stage + armor recommendation) should become its own chunk, preserving the relationship between the stage label and the item names. Alternatively, increasing chunk size to 800–1000 characters might capture both the section header and the associated table rows within the same chunk.

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**

The Chunking Strategy section of planning.md directly drove the implementation of `ingest.py`. Having pre-committed to 500-character chunks with 50-character overlap meant there was a concrete spec to verify against when generating the code, rather than picking numbers arbitrarily mid-implementation. It also made it easy to catch when chunks were splitting mid-word — the spec gave a clear standard to test the output against before moving to embedding.

**One way your implementation diverged from the spec, and why:**

The spec listed Guide:Walkthrough as source #3. During ingestion testing, the first chunk of that page read: "Issues: Most likely outdated since 1.4. Please do not use this guide." Since the goal was accurate, useful game knowledge, using a deprecated guide would undermine retrieval quality. It was replaced with the Hardmode page, which covers similar progression content without the quality warning. The planning.md Documents table was updated to reflect the change.

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- *What I gave the AI:* The Documents table (10 source URLs) and the Chunking Strategy section from planning.md (500-char chunks, 50-char overlap), plus the pipeline diagram.
- *What it produced:* A complete `ingest.py` script using `requests` and `BeautifulSoup` to fetch each URL, strip HTML, apply regex boilerplate removal, chunk the text, and save to `chunks.json` with source metadata.
- *What I changed or overrode:* The initial boilerplate removal patterns did not match the actual Terraria wiki HTML because `get_text()` inserts spaces between tags, breaking exact-match regex patterns. After running the script and seeing boilerplate in the first chunks, I directed the AI through several rounds of pattern fixes — switching from `.*?` to `[^.]*` matching and adding new patterns for each newly revealed banner. I also identified that Guide:Walkthrough was flagged as outdated and directed the replacement with the Hardmode page.

**Instance 2**

- *What I gave the AI:* The Retrieval Approach section from planning.md (all-MiniLM-L6-v2, top-k=5) and the pipeline diagram showing the query path through the Embedding Agent and ChromaDB.
- *What it produced:* `embed.py` with ChromaDB ingestion and a `query()` function, and `query.py` with a Groq-connected generation function and a system prompt.
- *What I changed or overrode:* The initial ChromaDB collection used default L2 distance. I directed the AI to switch to cosine distance (`hnsw:space: cosine`) so that distance scores would be interpretable against the milestone's 0.5 threshold. I also specified that source attribution must be extracted programmatically from chunk metadata rather than relying on the LLM to cite sources in its response.
