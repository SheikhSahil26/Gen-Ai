import asyncio

from ecommerce_ai.db.database import AsyncSessionLocal
from ecommerce_ai.repositories.product_repository import ProductRepository
from ecommerce_ai.tools.product_tools import create_product_tools


async def main():

    async with AsyncSessionLocal() as session:

        repository = ProductRepository(session)

        tools = create_product_tools(repository)

        search_tool = tools[0]

        result = await search_tool.ainvoke(
            {
                "request": {
                    "query": "gaming laptop",
                    "max_price": 70000,
                    "available_only": True,
                    "limit": 10,
                }
            }
        )

        for product in result:
            print(product)


if __name__ == "__main__":
    asyncio.run(main())