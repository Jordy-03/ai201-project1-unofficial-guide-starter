import json
from sentence_transformers import SentenceTransformer
import chromadb

CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "terraria"
TOP_K = 5


def load_and_embed():
    chunks = json.load(open("chunks.json", encoding="utf-8"))
    model = SentenceTransformer("all-MiniLM-L6-v2")

    client = chromadb.PersistentClient(path=CHROMA_PATH)
    # cosine distance so scores are interpretable (0 = identical, 1 = unrelated)
    collection = client.get_or_create_collection(
        COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )

    if collection.count() > 0:
        print(f"Collection already has {collection.count()} chunks — skipping embedding.")
        return collection, model

    print(f"Embedding {len(chunks)} chunks (this will take a few minutes on first run)...")
    texts = [c["text"] for c in chunks]
    embeddings = model.encode(texts, show_progress_bar=True)

    collection.add(
        ids=[str(i) for i in range(len(chunks))],
        embeddings=embeddings.tolist(),
        documents=texts,
        metadatas=[
            {"source": c["source"], "chunk_index": i}
            for i, c in enumerate(chunks)
        ]
    )
    print(f"Stored {len(chunks)} chunks in ChromaDB at '{CHROMA_PATH}/'.")
    return collection, model


def query(collection, model, question, k=TOP_K):
    q_embedding = model.encode([question])
    results = collection.query(
        query_embeddings=q_embedding.tolist(),
        n_results=k,
        include=["documents", "metadatas", "distances"]
    )
    return results


def print_results(question, results):
    print(f"\nQuery: {question}")
    print("-" * 70)
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0]
    ):
        source = meta["source"].split("/")[-1]
        print(f"  Source : {source}")
        print(f"  Distance: {dist:.3f}")
        print(f"  Text   : {doc[:200]}")
        print()


if __name__ == "__main__":
    collection, model = load_and_embed()

    test_questions = [
        "What item is used to manually summon the Eye of Cthulhu?",
        "What armor should a summoner player use in early Hardmode?",
        "What triggers a Blood Moon and what enemies does it spawn?",
    ]

    for question in test_questions:
        results = query(collection, model, question)
        print_results(question, results)
