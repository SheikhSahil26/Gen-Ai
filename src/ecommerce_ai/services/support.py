from ecommerce_ai.rag.retriever import (
    get_support_retriever,
)


class SupportService:

    def __init__(self):
        self.retriever = get_support_retriever()

    async def retrieve_knowledge(
        self,
        query: str,
    ):

        documents = await self.retriever.ainvoke(
            query
        )

        return [
            {
                "content": document.page_content,
                "metadata": document.metadata,
            }
            for document in documents
        ]