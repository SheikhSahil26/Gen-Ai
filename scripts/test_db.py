import asyncio

from sqlalchemy.ext.asyncio import create_async_engine

from ecommerce_ai.config.settings import settings


async def main():
    engine = create_async_engine(settings.database_url)

    async with engine.connect():
        print("DATABASE CONNECTION SUCCESSFUL")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())