import asyncio

from ecommerce_ai.classifiers.intent_classifier import (
    IntentClassifier,
)


async def main():

    classifier = IntentClassifier()

    queries = [
        "I want to compare lenovo and dell laptops.",
        "I want to buy a laptop",
        "Where is my order?"
    ]

    for query in queries:

        print("\n" + "=" * 60)
        print(f"QUERY: {query}")

        result = await classifier.classify(query)

        print(
            f"INTENT: {result.intent}"
        )

        print(
            f"CONFIDENCE: {result.confidence}"
        )


if __name__ == "__main__":
    asyncio.run(main())