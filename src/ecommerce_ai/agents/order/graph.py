from langchain_core.messages import SystemMessage
from langgraph.graph import END, START, StateGraph

from ecommerce_ai.agents.order.agent import create_order_agent
from ecommerce_ai.agents.order.prompts import ORDER_AGENT_SYSTEM_PROMPT
from ecommerce_ai.agents.order.state import OrderAgentState
from ecommerce_ai.repositories.order_repository import OrderRepository
from ecommerce_ai.repositories.shopping_repository import ShoppingRepository
from ecommerce_ai.tools.limited_tool_node import (
    create_limited_tool_runner,
    route_after_limited_tools,
)


def create_order_graph(
    repository: OrderRepository,
    shopping_repository: ShoppingRepository | None = None,
):
    model, tools = create_order_agent(repository, shopping_repository)
    tool_node = create_limited_tool_runner(tools)

    async def order_llm(state: OrderAgentState):
        messages = state["messages"]
        messages_with_system = [
            SystemMessage(content=ORDER_AGENT_SYSTEM_PROMPT),
            *messages,
        ]
        response = await model.ainvoke(messages_with_system)
        return {"messages": [response]}

    def should_continue(state: OrderAgentState):
        last_message = state["messages"][-1]
        if last_message.tool_calls:
            return "tools"
        return END

    graph = StateGraph(OrderAgentState)
    graph.add_node("order_llm", order_llm)
    graph.add_node("order_tools", tool_node)

    graph.add_edge(START, "order_llm")
    graph.add_conditional_edges(
        "order_llm",
        should_continue,
        {
            "tools": "order_tools",
            END: END,
        },
    )
    graph.add_conditional_edges(
        "order_tools",
        route_after_limited_tools,
        {"llm": "order_llm", "end": END},
    )

    return graph.compile()
