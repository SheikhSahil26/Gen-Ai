from ecommerce_ai.rag.vector_store import get_vector_store


def get_support_retriever():

    vector_store = get_vector_store()

    return vector_store.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": 4,
            "fetch_k": 10,
            "lambda_mult": 0.5,
        },
    )