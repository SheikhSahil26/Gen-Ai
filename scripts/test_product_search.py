import asyncio

from ecommerce_ai.db.database import AsyncSessionLocal
from ecommerce_ai.repositories.product_repository import ProductRepository
from ecommerce_ai.schemas.products import ProductSearchRequest


async def main():

    async with AsyncSessionLocal() as session:

        repository = ProductRepository(session)

        request = ProductSearchRequest(
            query="laptop",
            max_price=70000,
            available_only=True,
            limit=10,
        )

        products = await repository.search_products(request)

        print("database result after user query")

        for product in products:
            print("database result after user query",
                product.id,
                product.name,
                product.brand,
            )


if __name__ == "__main__":
    asyncio.run(main())