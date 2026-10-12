import asyncio

from langchain_core.messages import HumanMessage

from ecommerce_ai.agents.product.graph import create_product_graph
from ecommerce_ai.db.database import AsyncSessionLocal
from ecommerce_ai.repositories.product_repository import ProductRepository


async def main():

    async with AsyncSessionLocal() as session:

        repository = ProductRepository(session)

        graph = create_product_graph(repository)

        result = await graph.ainvoke(
            {
                "messages": [
                    HumanMessage(
                        content="best smartphones under 30000"
                    )
                ]
            }
        )

        print("\n" + "=" * 60)
        print("PRODUCT AGENT RESULT")
        print("=" * 60)

        for message in result["messages"]:

            print("\nTYPE:")
            print(type(message).__name__)

            print("\nCONTENT:")
            print(message.content)

            if getattr(message, "tool_calls", None):
                print("\nTOOL CALLS:")
                print(message.tool_calls)


if __name__ == "__main__":
    asyncio.run(main())