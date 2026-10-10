
from functools import lru_cache

from sentence_transformers import SentenceTransformer


@lru_cache(maxsize=1)
def get_model():
    print("Loading smaller embedding model...", flush=True)

    model = SentenceTransformer(
        "sentence-transformers/paraphrase-MiniLM-L3-v2",
        device="cpu",
    )

    print("Embedding model loaded successfully.", flush=True)
    return model


def create_embedding(text: str):
    model = get_model()

    embedding = model.encode(
        text,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    )

    return embedding.tolist()


def create_embeddings(texts: list[str]):
    if not texts:
        return []

    model = get_model()

    embeddings = model.encode(
        texts,
        batch_size=1,
        show_progress_bar=False,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )

    return embeddings.tolist()
