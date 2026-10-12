import asyncio

from ecommerce_ai.graph.graph import app_graph


async def main():

    thread_id = "test-conversation-1"

    # ============================================================
    # TURN 1
    # ============================================================

    result = await app_graph.ainvoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "Find me a Lenovo gaming laptop under 70000.",
                }
            ]
        },
        {
            "configurable": {
                "thread_id": thread_id,
            }
        },
    )

    print("\n================ TURN 1 ================\n")
    print(result)

    # ============================================================
    # TURN 2
    # ============================================================

    result = await app_graph.ainvoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "Add the first one to my cart.",
                }
            ]
        },
        {
            "configurable": {
                "thread_id": thread_id,
            }
        },
    )

    print("\n================ TURN 2 ================\n")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())