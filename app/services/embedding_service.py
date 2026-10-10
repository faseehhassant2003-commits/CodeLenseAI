
from functools import lru_cache

from sentence_transformers import SentenceTransformer


@lru_cache(maxsize=1)
def get_model():
    """Load the embedding model only when first needed."""
    return SentenceTransformer(
        "all-MiniLM-L6-v2",
        device="cpu",
    )


def generate_embedding(text: str):
    """Generate an embedding for the supplied text."""
    model = get_model()
    return model.encode(text).tolist()
