from sentence_transformers import SentenceTransformer


model = SentenceTransformer("all-MiniLM-L6-v2")


def create_embedding(text: str):
    """
    Create an embedding for a single text.
    Used for user questions during RAG retrieval.
    """
    embedding = model.encode(text)

    return embedding.tolist()


def create_embeddings(texts: list[str]):
    """
    Create embeddings for multiple texts in batches.
    Used during repository ingestion.
    """
    embeddings = model.encode(
        texts,
        batch_size=32,
        show_progress_bar=True
    )

    return embeddings.tolist()