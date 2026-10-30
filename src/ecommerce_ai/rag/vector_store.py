from functools import lru_cache

from langchain_qdrant import QdrantVectorStore

from ecommerce_ai.config.settings import settings
from ecommerce_ai.rag.embeddings import get_embedding_model


@lru_cache(maxsize=1)
def get_vector_store() -> QdrantVectorStore:
    """Connect to the pre-created support collection in Qdrant."""
    return QdrantVectorStore.from_existing_collection(
        collection_name=settings.qdrant_collection,
        embedding=get_embedding_model(),
        url=settings.qdrant_url,
        api_key=settings.qdrant_api_key or None,
    )
