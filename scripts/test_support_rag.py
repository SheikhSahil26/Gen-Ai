from ecommerce_ai.rag.retriever import get_support_retriever
import dotenv
from dotenv import load_dotenv

load_dotenv()

async def main():

    retriever = get_support_retriever()

    query = "My product arrived damaged. What should I do?"

    documents = await retriever.ainvoke(query)

    print("\nRetrieved documents:\n")

    for index, document in enumerate(documents, start=1):

        print("=" * 80)
        print(f"DOCUMENT {index}")
        print("=" * 80)

        print("Metadata:")
        print(document.metadata)

        print("\nContent:")
        print(document.page_content)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())