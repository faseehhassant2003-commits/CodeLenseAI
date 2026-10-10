
from functools import lru_cache

from sentence_transformers import SentenceTransformer


@lru_cache(maxsize=1)
def get_model():
    """Load the embedding model only when first needed."""
    return SentenceTransformer(
        "all-MiniLM-L6-v2",
        device="cpu",
    )


def create_embedding(text: str):
    """Create an embedding for one text."""
    model = get_model()
    return model.encode(text).tolist()


def create_embeddings(texts: list[str]):
    """Create embeddings for multiple texts."""
    model = get_model()
    return model.encode(texts).tolist()
