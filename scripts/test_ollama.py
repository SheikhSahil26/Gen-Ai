import asyncio

from langchain_ollama import ChatOllama


async def main():

    model = ChatOllama(
        model="gpt-oss:120b-cloud",
        temperature=0,
    )

    response = await model.ainvoke(
        "Explain what a database repository is in one sentence."
    )

    print("Response:")
    print(response.content)


if __name__ == "__main__":
    asyncio.run(main())