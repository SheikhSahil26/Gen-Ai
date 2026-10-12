import json

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage

from langgraph.graph import END, START, StateGraph

from ecommerce_ai.agents.product.agent import create_product_agent
from ecommerce_ai.agents.product.prompts import (
    PRODUCT_AGENT_SYSTEM_PROMPT,
)
from ecommerce_ai.agents.product.state import ProductAgentState
from ecommerce_ai.repositories.product_repository import ProductRepository
from ecommerce_ai.tools.limited_tool_node import (
    create_limited_tool_runner,
    route_after_limited_tools,
)


def create_product_graph(
    repository: ProductRepository,
):

    # --------------------------------
    # Create Product Agent
    # --------------------------------

    model, tools = create_product_agent(repository)

    # --------------------------------
    # Create Tool Node
    # --------------------------------

    tool_node = create_limited_tool_runner(tools)

    # --------------------------------
    # LLM Node
    # --------------------------------

    async def product_llm(
        state: ProductAgentState,
    ):

        messages = state["messages"]

        # Treat the search tool as the only source for product suggestions.
        # Ask the user to choose from verified matches before continuing.
        recent_messages = []
        for message in reversed(messages):
            # Ignore search results from earlier user turns.
            if isinstance(message, HumanMessage):
                break
            if isinstance(message, AIMessage) and message.tool_calls:
                break
            if isinstance(message, ToolMessage):
                recent_messages.append(message)

        search_results = [
            message
            for message in recent_messages
            if message.name == "search_products"
        ]
        if search_results:
            def decode_result(message):
                content = message.content
                if content == []:
                    return []
                if isinstance(content, str):
                    try:
                        return json.loads(content)
                    except json.JSONDecodeError:
                        return None
                if isinstance(content, list):
                    if all(
                        isinstance(part, dict) and part.get("type") == "text"
                        for part in content
                    ):
                        text_content = "\n".join(
                            part.get("text", "") for part in content
                        )
                        try:
                            return json.loads(text_content)
                        except json.JSONDecodeError:
                            return None
                    return content
                if isinstance(content, dict):
                    return content
                return None

            decoded_results = [
                decode_result(message)
                for message in search_results
            ]
            if any(result is None for result in decoded_results):
                return {
                    "messages": [
                        AIMessage(
                            content=(
                                "I couldn't verify the catalog search results, "
                                "so I can't safely suggest products right now. "
                                "Please try the search again."
                            )
                        )
                    ]
                }

            products = [
                product
                for result in decoded_results
                for product in (result if isinstance(result, list) else [])
                if isinstance(product, dict)
            ]
            if not products:
                return {
                    "messages": [
                        AIMessage(
                            content=(
                                "I couldn't find matching products in the "
                                "catalog. Would you like me to broaden or "
                                "change the search?"
                            )
                        )
                    ]
                }

            lines = ["These are the matching products currently in the catalog:"]
            for product in products:
                name = product.get("name", "Unnamed product")
                brand = product.get("brand")
                price = product.get("price")
                rating = product.get("rating")
                variant = product.get("variant_name")
                description = product.get("description")

                details = []
                if brand:
                    details.append(f"Brand: {brand}")
                if variant:
                    details.append(f"Variant: {variant}")
                if price is not None:
                    details.append(f"Price: {price}")
                if rating is not None:
                    details.append(f"Rating: {rating}")
                if description:
                    details.append(f"Description: {description}")

                detail_text = f" ({'; '.join(details)})" if details else ""
                lines.append(f"- {name}{detail_text}")

            lines.append("Which of these would you like to know more about?")
            return {"messages": [AIMessage(content="\n".join(lines))]}

        messages_with_system_prompt = [
            SystemMessage(
                content=PRODUCT_AGENT_SYSTEM_PROMPT
            ),
            *messages,
        ]

        response = await model.ainvoke(
            messages_with_system_prompt
        )

        print(response,"this is respose in graph")

        return {
            "messages": [response]
        }

    # --------------------------------
    # Router
    # --------------------------------

    def should_continue(
        state: ProductAgentState,
    ):

        last_message = state["messages"][-1]

        print(last_message,"this is last message!!!!")

        if last_message.tool_calls:
            return "tools"

        return END

    # --------------------------------
    # Create Graph
    # --------------------------------

    graph = StateGraph(ProductAgentState)

    # --------------------------------
    # Add Nodes
    # --------------------------------

    graph.add_node(
        "product_llm",
        product_llm,
    )

    graph.add_node(
        "product_tools",
        tool_node,
    )

    # --------------------------------
    # START → LLM
    # --------------------------------

    graph.add_edge(
        START,
        "product_llm",
    )

    # --------------------------------
    # LLM → Tool OR END
    # --------------------------------

    graph.add_conditional_edges(
        "product_llm",
        should_continue,
        {
            "tools": "product_tools",
            END: END,
        },
    )

    # --------------------------------
    # Tool → LLM
    # --------------------------------

    graph.add_conditional_edges(
        "product_tools",
        route_after_limited_tools,
        {"llm": "product_llm", "end": END},
    )

    # --------------------------------
    # Compile
    # --------------------------------

    return graph.compile()