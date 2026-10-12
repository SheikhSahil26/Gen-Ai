from functools import lru_cache

from langchain_chroma import Chroma

from ecommerce_ai.rag.embeddings import get_embedding_model


COLLECTION_NAME = "ecommerce_support"


@lru_cache(maxsize=1)
def get_vector_store() -> Chroma:

    embeddings = get_embedding_model()

    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory="./data/chroma",
    )