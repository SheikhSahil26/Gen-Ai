from typing import Any, Literal

from langgraph.graph import MessagesState


OrderIntent = Literal[
    "track_order",
    "get_last_order",
    "get_order_history",
    "get_order_details",
    "compare_order_with_cart",
    "search_past_orders",
    "cancel_order",
    "checkout",
    "place_order",
    "get_addresses",
    "reorder",
    "unknown",
]

OrderWorkflowStatus = Literal[
    "idle",
    "understanding_request",
    "looking_up_order",
    "tracking_shipment",
    "loading_order_history",
    "preparing_checkout",
    "awaiting_confirmation",
    "validating_order",
    "placing_order",
    "cancelling_order",
    "reordering",
    "completed",
    "cancelled",
    "failed",
]


class OrderAgentState(MessagesState, total=False):
    """Shared state for order lookup, fulfillment, and checkout workflows."""

    # Request and identity context
    user_id: int | None
    session_id: str | None
    original_query: str | None
    current_query: str | None
    request_intent: OrderIntent
    order_number: str | None
    tracking_number: str | None
    product_name: str | None
    status_filter: str | None
    result_limit: int

    # Order lookup and history results
    selected_order: dict[str, Any] | None
    order_history: list[dict[str, Any]]
    order_details: dict[str, Any] | None
    order_search_results: list[dict[str, Any]]
    order_found: bool | None
    order_status: str | None

    # Shipment and tracking context
    shipment_details: list[dict[str, Any]]
    shipment_status: str | None
    carrier: str | None
    estimated_delivery: str | None
    tracking_result: dict[str, Any] | None

    # Checkout preview and pricing
    checkout_status: Literal[
        "not_started",
        "preparing",
        "ready_for_confirmation",
        "blocked",
        "placing",
        "placed",
        "cancelled",
        "failed",
    ]
    checkout_preview: dict[str, Any] | None
    checkout_items: list[dict[str, Any]]
    subtotal: str | None
    discount_total: str | None
    shipping_fee: str | None
    tax_amount: str | None
    total_amount: str | None
    currency: str | None
    address_id: int | None
    delivery_address: str | None
    payment_method: str | None

    # Human-in-the-loop approval state
    confirmation_required: bool
    confirmation_received: bool
    confirmation_response: Literal[
        "yes",
        "no",
        "unclear",
        "not_requested",
    ]
    pending_action: dict[str, Any] | None
    order_placement_result: dict[str, Any] | None

    # Cancellation and reorder outcomes
    cancellation_result: dict[str, Any] | None
    reorder_result: dict[str, Any] | None
    operation_success: bool | None
    operation_message: str | None

    # Tool execution and safety controls
    last_tool: str | None
    last_tool_call_id: str | None
    tool_execution_status: Literal[
        "not_started",
        "running",
        "succeeded",
        "failed",
        "limit_reached",
    ]
    tool_call_count: int
    tool_limit_reached: bool
    tool_results: list[dict[str, Any]]

    # Validation, clarification, and errors
    validation_status: Literal[
        "not_checked",
        "valid",
        "invalid",
        "requires_revalidation",
    ]
    validation_errors: list[str]
    clarification_required: bool
    clarification_question: str | None
    error: str | None
    error_code: str | None
    retryable: bool

    # Agent workflow and final response
    status: OrderWorkflowStatus
    next_action: Literal[
        "track",
        "view_history",
        "view_details",
        "compare",
        "search",
        "prepare_checkout",
        "request_confirmation",
        "place_order",
        "cancel_order",
        "reorder",
        "clarify",
        "respond",
        "end",
    ] | None
    response: str | None
