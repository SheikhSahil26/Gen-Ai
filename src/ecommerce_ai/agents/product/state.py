from typing import Any, Literal
from langgraph.graph import MessagesState
from typing_extensions import NotRequired


class ProductAgentState(MessagesState):

    # ============================================================
    # REQUEST / USER CONTEXT
    # ============================================================

    user_id: int | None
    session_id: str | None

    original_query: str | None
    current_query: str | None

    # ============================================================
    # SEARCH / FILTER STATE
    # ============================================================

    search_request: dict[str, Any] | None

    search_query: str | None
    category: str | None
    brand: str | None

    min_price: float | None
    max_price: float | None

    specifications: dict[str, Any]

    available_only: bool

    sort_by: str | None
    sort_order: Literal["asc", "desc"] | None

    limit: int
    offset: int

    # ============================================================
    # SEARCH EXECUTION STATE
    # ============================================================

    search_performed: bool
    search_attempts: int

    search_results: list[dict[str, Any]]
    result_count: int

    has_more_results: bool

    # ============================================================
    # PRODUCT / VARIANT SELECTION
    # ============================================================

    selected_product_id: int | None
    selected_variant_id: int | None

    selected_product: dict[str, Any] | None
    selected_variant: dict[str, Any] | None

    # ============================================================
    # COMPARISON STATE
    # ============================================================

    comparison_product_ids: list[int]
    comparison_results: list[dict[str, Any]]

    # ============================================================
    # FOLLOW-UP / CONTEXT STATE
    # ============================================================

    referenced_product_id: int | None
    referenced_variant_id: int | None

    clarification_required: bool
    clarification_question: str | None

    # ============================================================
    # TOOL EXECUTION STATE
    # ============================================================

    last_tool: str | None
    last_tool_call_id: str | None
    tool_execution_status: Literal[
        "not_started",
        "running",
        "success",
        "failed",
    ]

    # ============================================================
    # WORKFLOW STATE
    # ============================================================

    status: Literal[
        "idle",
        "understanding_request",
        "searching",
        "processing_results",
        "awaiting_clarification",
        "awaiting_selection",
        "showing_results",
        "comparing",
        "completed",
        "failed",
    ]

    next_action: Literal[
        "search",
        "get_details",
        "get_variants",
        "check_availability",
        "compare",
        "clarify",
        "respond",
        "end",
    ] | None

    # ============================================================
    # ERROR STATE
    # ============================================================

    error: str | None
    error_code: str | None
    retryable: bool

    # ============================================================
    # RESPONSE STATE
    # ============================================================

    response: str | None

    # ============================================================
    # AGENT METADATA
    # ============================================================

    agent_name: str
    agent_version: str | None

    tool_call_count: NotRequired[int]
    tool_limit_reached: NotRequired[bool]