from langchain_core.tools import tool

from ecommerce_ai.services.support import SupportService


def create_support_tools():

    service = SupportService()

    @tool
    async def search_support_knowledge(
        query: str,
    ):
        """
        Search the official e-commerce support knowledge base
        for policies, FAQs, troubleshooting information,
        returns, refunds, cancellation, delivery, warranty,
        payment, and other support information.
        """

        return await service.retrieve_knowledge(
            query=query
        )

    return [
        search_support_knowledge,
    ]