from langchain_core.messages import AIMessage, ToolMessage
from langgraph.prebuilt import ToolNode

MAX_TOOL_CALLS_PER_AGENT = 5


def create_limited_tool_runner(tools):
    """Create a ToolNode runner that caps tool calls per agent invocation."""
    tool_node = ToolNode(tools)

    async def run_tools(state):
        calls = state["messages"][-1].tool_calls
        calls_used = state.get("tool_call_count", 0)

        if calls_used + len(calls) > MAX_TOOL_CALLS_PER_AGENT:
            tool_messages = [
                ToolMessage(
                    content=(
                        "Tool call limit reached. Do not make another tool call. "
                        "Respond using the information already available and ask "
                        "the user to narrow the request if needed."
                    ),
                    tool_call_id=call["id"],
                    name=call["name"],
                )
                for call in calls
            ]
            return {
                "messages": [
                    *tool_messages,
                    AIMessage(
                        content=(
                            f"I stopped before running another lookup because this "
                            f"request would exceed the limit of "
                            f"{MAX_TOOL_CALLS_PER_AGENT} tool calls. Please narrow "
                            "the request to a category or a specific product, and "
                            "I can continue."
                        )
                    ),
                ],
                "tool_call_count": calls_used,
                "tool_limit_reached": True,
            }

        result = await tool_node.ainvoke(state)
        return {
            **result,
            "tool_call_count": calls_used + len(calls),
            "tool_limit_reached": False,
        }

    return run_tools


def route_after_limited_tools(state):
    return "end" if state.get("tool_limit_reached") else "llm"
