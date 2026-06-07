import os
from dotenv import load_dotenv
from groq import Groq
import chromadb
from sentence_transformers import SentenceTransformer

load_dotenv()

_model = SentenceTransformer("all-MiniLM-L6-v2")
_client = chromadb.PersistentClient(path="chroma_db")
_collection = _client.get_collection("terraria")
_groq = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """You are a Terraria game guide assistant.

Answer the user's question using ONLY the information in the provided context. Do not use any knowledge from outside the provided documents.

If the context does not contain enough information to answer the question, respond with exactly:
"I don't have enough information in my documents to answer that."

Do not make up items, stats, or mechanics. Do not add information that is not present in the context."""


def ask(question, k=5):
    # Retrieve top-k relevant chunks
    q_embedding = _model.encode([question])
    results = _collection.query(
        query_embeddings=q_embedding.tolist(),
        n_results=k,
        include=["documents", "metadatas", "distances"]
    )

    chunks = results["documents"][0]
    metadatas = results["metadatas"][0]

    # Build context block — label each chunk with its source
    context = "\n\n".join(
        f"[Source: {meta['source'].split('/')[-1]}]\n{chunk}"
        for chunk, meta in zip(chunks, metadatas)
    )

    response = _groq.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
        ]
    )

    answer = response.choices[0].message.content

    # Programmatic source attribution — extracted from metadata, not from the LLM
    sources = list({meta["source"].split("/")[-1] for meta in metadatas})

    return {"answer": answer, "sources": sources}
