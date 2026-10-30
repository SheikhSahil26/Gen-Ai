"""Copy the support collection from local Chroma into a new Qdrant collection.

Run from the project root after setting QDRANT_URL and (for Qdrant Cloud)
QDRANT_API_KEY. The script never deletes or modifies the Chroma source. It
refuses to overwrite an existing Qdrant collection so a migration cannot
silently replace destination data.
"""

from uuid import NAMESPACE_URL, uuid5

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

from ecommerce_ai.config.settings import settings
from ecommerce_ai.rag.embeddings import get_embedding_model


CHROMA_COLLECTION = "ecommerce_support"
CHROMA_PATH = "./data/chroma"


def main() -> None:
    embeddings = get_embedding_model()
    chroma = Chroma(
        collection_name=CHROMA_COLLECTION,
        embedding_function=embeddings,
        persist_directory=CHROMA_PATH,
    )
    records = chroma.get(include=["documents", "metadatas"])
    old_ids = records.get("ids", [])
    texts = records.get("documents", [])
    metadatas = records.get("metadatas", [])

    if not old_ids or not texts or len(old_ids) != len(texts):
        raise RuntimeError(
            f"Chroma collection {CHROMA_COLLECTION!r} is empty or inconsistent. "
            "Check the local data/chroma directory before migrating."
        )

    qdrant_client = QdrantClient(
        url=settings.qdrant_url,
        api_key=settings.qdrant_api_key or None,
    )
    try:
        if qdrant_client.collection_exists(settings.qdrant_collection):
            raise RuntimeError(
                f"Qdrant collection {settings.qdrant_collection!r} already exists. "
                "Choose a new QDRANT_COLLECTION name to avoid overwriting data."
            )

        documents = [
            Document(
                page_content=text,
                metadata=metadata or {},
            )
            for text, metadata in zip(texts, metadatas or [{}] * len(texts))
            if text is not None
        ]
        ids = [
            str(uuid5(NAMESPACE_URL, f"chroma:{old_id}"))
            for old_id, text in zip(old_ids, texts)
            if text is not None
        ]

        store = QdrantVectorStore.from_documents(
            documents=documents,
            embedding=embeddings,
            ids=ids,
            collection_name=settings.qdrant_collection,
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key or None,
        )
        migrated_count = store.client.count(
            collection_name=settings.qdrant_collection,
            exact=True,
        ).count
        if migrated_count != len(documents):
            raise RuntimeError(
                f"Expected {len(documents)} points in Qdrant, found {migrated_count}."
            )

        print(
            f"Migrated {migrated_count} documents from Chroma "
            f"{CHROMA_COLLECTION!r} to Qdrant {settings.qdrant_collection!r}."
        )
        print("The Chroma source was left unchanged.")
    finally:
        qdrant_client.close()


if __name__ == "__main__":
    main()
