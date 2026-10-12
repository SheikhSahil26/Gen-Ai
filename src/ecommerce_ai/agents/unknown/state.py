from typing import Literal
from langgraph.graph import MessagesState
from typing_extensions import NotRequired

class UnknownAgentState(MessagesState, total=False):
    """State for requests that do not map to a store workflow."""
    original_query: NotRequired[str]
    response_kind: NotRequired[Literal["greeting", "redirect", "clarification"]]
    response: NotRequired[str]
