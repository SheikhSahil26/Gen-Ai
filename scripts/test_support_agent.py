import asyncio
import dotenv
from dotenv import load_dotenv

load_dotenv()

from ecommerce_ai.agents.support.agent import (
    create_support_agent,
)


async def main():

    support_agent = create_support_agent()

    result = await support_agent.ainvoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "My product arrived damaged. "
                        "What should I do?"
                    ),
                }
            ]
        }
    )

    print("\n==============================")
    print("SUPPORT AGENT RESULT")
    print("==============================")

    print("\nIntent:")
    print(
        result.get("support_intent")
    )

    print("\nSearch Query:")
    print(
        result.get("search_query")
    )

    print("\nRetrieval Confidence:")
    print(
        result.get("retrieval_confidence")
    )

    print("\nAnswer:")
    print(
        result.get("grounded_answer")
    )

    print("\nEscalation:")
    print(
        result.get("requires_escalation")
    )

    print("\nCitations:")
    print(
        result.get("citations")
    )


if __name__ == "__main__":
    asyncio.run(main())