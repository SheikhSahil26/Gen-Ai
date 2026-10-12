from langchain_core.messages import SystemMessage
from langgraph.graph import END, START, StateGraph
from ecommerce_ai.agents.unknown.prompts import UNKNOWN_AGENT_SYSTEM_PROMPT
from ecommerce_ai.agents.unknown.state import UnknownAgentState

def create_unknown_graph(model):
    async def respond_to_unknown_request(state: UnknownAgentState):
        query = state["messages"][-1].content if state.get("messages") else ""
        response = await model.ainvoke(
            [SystemMessage(content=UNKNOWN_AGENT_SYSTEM_PROMPT), *state.get("messages", [])]
        )
        return {
            "messages": [response],
            "original_query": query if isinstance(query, str) else str(query),
            "response": response.content,
        }
    graph = StateGraph(UnknownAgentState)
    graph.add_node("respond_to_unknown_request", respond_to_unknown_request)
    graph.add_edge(START, "respond_to_unknown_request")
    graph.add_edge("respond_to_unknown_request", END)
    return graph.compile()
