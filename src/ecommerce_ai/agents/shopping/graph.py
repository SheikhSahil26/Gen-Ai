from langchain_core.messages import SystemMessage
from langgraph.graph import END, START, StateGraph

from ecommerce_ai.agents.shopping.agent import create_shopping_agent
from ecommerce_ai.agents.shopping.prompts import SHOPPING_AGENT_SYSTEM_PROMPT
from ecommerce_ai.agents.shopping.state import ShoppingAgentState
from ecommerce_ai.repositories.product_repository import ProductRepository
from ecommerce_ai.repositories.shopping_repository import ShoppingRepository
from ecommerce_ai.tools.limited_tool_node import (
    create_limited_tool_runner,
    route_after_limited_tools,
)


def create_shopping_graph(repository: ShoppingRepository, product_repository: ProductRepository):
    model, tools = create_shopping_agent(repository, product_repository)
    tool_node = create_limited_tool_runner(tools)

    async def shopping_llm(state: ShoppingAgentState):
        response = await model.ainvoke([
            SystemMessage(content=SHOPPING_AGENT_SYSTEM_PROMPT),
            *state["messages"],
        ])
        return {"messages": [response]}

    def should_continue(state: ShoppingAgentState):
        return "tools" if state["messages"][-1].tool_calls else END

    graph = StateGraph(ShoppingAgentState)
    graph.add_node("shopping_llm", shopping_llm)
    graph.add_node("shopping_tools", tool_node)
    graph.add_edge(START, "shopping_llm")
    graph.add_conditional_edges("shopping_llm", should_continue, {"tools": "shopping_tools", END: END})
    graph.add_conditional_edges(
        "shopping_tools",
        route_after_limited_tools,
        {"llm": "shopping_llm", "end": END},
    )
    return graph.compile()
