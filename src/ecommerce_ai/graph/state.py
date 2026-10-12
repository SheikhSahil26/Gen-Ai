from typing import Annotated, Any, TypedDict
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages
from typing_extensions import NotRequired


class EcommerceState(TypedDict):
    """
    Global state shared by the Supervisor and all domain agents.
    """

    # -------------------------
    # Conversation
    # -------------------------

    messages: Annotated[list[AnyMessage], add_messages]

    original_query: NotRequired[str]
    resolved_query: NotRequired[str]

    # -------------------------
    # Intent / Task Management
    # -------------------------

    intents: NotRequired[list[str]]
    intent_confidence: NotRequired[float]
    """
    All intents detected for the current user request.

    Example:
    ["product", "shopping"]
    """

    planned_tasks: NotRequired[list[dict[str, Any]]]

    task_queue: NotRequired[list[dict[str, Any]]]
    """
    Intent tasks still waiting to be executed.

    Example:
    [{"agent": "shopping", "status": "pending"}]
    """

    current_task: NotRequired[dict[str, Any] | None]
    """
    Task currently being executed.

    Example:
    "product"
    """

    completed_tasks: NotRequired[list[dict[str, Any]]]
    """
    Tasks already completed.

    Example:
    [{"agent": "product", "status": "completed"}]
    """

    failed_tasks: NotRequired[list[str]]

    # -------------------------
    # Supervisor Routing
    # -------------------------

    next_worker: NotRequired[str]
    """
    Agent selected by the supervisor.

    product | shopping | order | support | end
    """

    # -------------------------
    # Cross-Agent Context
    # -------------------------

    active_product_context: NotRequired[list[dict[str, Any]]]

    active_order_context: NotRequired[dict[str, Any]]

    active_cart_context: NotRequired[dict[str, Any]]

    entities: NotRequired[dict[str, Any]]

    # -------------------------
    # Execution Control
    # -------------------------

    loop_count: NotRequired[int]

    # -------------------------
    # Final Response
    # -------------------------

    response_parts: NotRequired[list[str]]

    final_response: NotRequired[str]