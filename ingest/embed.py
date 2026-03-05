import voyageai
from supabase import create_client
from app.config import VOYAGE_API_KEY, SUPABASE_URL, SUPABASE_KEY

voyage_client = voyageai.Client(api_key=VOYAGE_API_KEY)
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

BATCH_SIZE = 20  # Voyage AI batch limit


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed a list of texts in batches."""
    all_embeddings = []
    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i:i + BATCH_SIZE]
        result = voyage_client.embed(batch, model="voyage-3", input_type="document")
        all_embeddings.extend(result.embeddings)
    return all_embeddings


def store_chunks(
    chunks: list[str],
    embeddings: list[list[float]],
    source_type: str,
    source_file: str = "",
    category: str = "",
    topic: str = "",
    metadata: dict = None,
):
    """Store chunks with their embeddings in Supabase."""
    for chunk_text, embedding in zip(chunks, embeddings):
        row = {
            "content": chunk_text,
            "embedding": embedding,
            "source_type": source_type,
            "source_file": source_file,
            "category": category,
            "topic": topic,
            "metadata": metadata or {},
        }
        supabase.table("chunks").insert(row).execute()


def ingest_and_store(
    chunks: list[str],
    source_type: str,
    source_file: str = "",
    category: str = "",
    topic: str = "",
    metadata: dict = None,
):
    """Embed and store chunks in one step."""
    if not chunks:
        return 0

    print(f"  Embedding {len(chunks)} chunks...")
    embeddings = embed_texts(chunks)
    print(f"  Storing in database...")
    store_chunks(chunks, embeddings, source_type, source_file, category, topic, metadata)
    print(f"  Done: {len(chunks)} chunks stored.")
    return len(chunks)
