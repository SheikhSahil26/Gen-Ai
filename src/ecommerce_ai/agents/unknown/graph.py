import asyncio
from langchain_core.messages import AIMessage, SystemMessage
from langgraph.graph import END, START, StateGraph
from ecommerce_ai.agents.unknown.prompts import UNKNOWN_AGENT_SYSTEM_PROMPT
from ecommerce_ai.agents.unknown.state import UnknownAgentState

GREETINGS = {
    "hi", "hello", "hey", "hey there", "hi there", "hello there",
    "good morning", "good afternoon", "good evening", "howdy",
    "sup", "whats up", "what's up", "help", "who are you",
    "what can you do", "hi bot", "hello bot",
}

GREETING_RESPONSE = (
    "Hello! Welcome to Common Goods! How can I help you today? "
    "You can ask me to search for products (like laptops or phones), "
    "manage your cart, check your recent orders, or ask about our return policies."
)

def create_unknown_graph(model):
    async def respond_to_unknown_request(state: UnknownAgentState):
        query = state["messages"][-1].content if state.get("messages") else ""
        query_str = query if isinstance(query, str) else str(query)
        cleaned = "".join(c for c in query_str.lower() if c.isalnum() or c.isspace()).strip()

        # Instant response for greetings — avoids slow cloud LLM call and timeouts
        if cleaned in GREETINGS:
            response = AIMessage(content=GREETING_RESPONSE)
            return {
                "messages": [response],
                "original_query": query_str,
                "response": response.content,
            }

        try:
            response = await asyncio.wait_for(
                model.ainvoke(
                    [SystemMessage(content=UNKNOWN_AGENT_SYSTEM_PROMPT), *state.get("messages", [])]
                ),
                timeout=35.0,
            )
        except Exception:
            response = AIMessage(
                content=(
                    "I can help with products, your cart, checkout, orders, "
                    "or store support. What would you like to do?"
                )
            )

        return {
            "messages": [response],
            "original_query": query_str,
            "response": response.content,
        }
    graph = StateGraph(UnknownAgentState)
    graph.add_node("respond_to_unknown_request", respond_to_unknown_request)
    graph.add_edge(START, "respond_to_unknown_request")
    graph.add_edge("respond_to_unknown_request", END)
    return graph.compile()
