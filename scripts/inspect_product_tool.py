from ecommerce_ai.db.database import AsyncSessionLocal
from ecommerce_ai.repositories.product_repository import ProductRepository
from ecommerce_ai.tools.product_tools import create_product_tools


async def main():

    async with AsyncSessionLocal() as session:

        repository = ProductRepository(session)

        tools = create_product_tools(repository)

        search_tool = tools[0]

        print("Tool name:")
        print(search_tool.name)

        print("\nTool description:")
        print(search_tool.description)

        print("\nTool arguments:")
        print(search_tool.args_schema.model_json_schema())


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())