from typing import Any, Literal

from langgraph.graph import MessagesState


class ShoppingAgentState(MessagesState, total=False):

    tool_call_count: int
    tool_limit_reached: bool

    # ============================================================
    # REQUEST / CONVERSATION CONTEXT
    # ============================================================

    original_query: str | None
    current_query: str | None

    # ============================================================
    # SHOPPING INTENT
    # ============================================================

    shopping_intent: Literal[
        "view_cart",
        "add_to_cart",
        "update_cart",
        "remove_from_cart",
        "clear_cart",
        "view_wishlist",
        "add_to_wishlist",
        "remove_from_wishlist",
        "clear_wishlist",
        "unknown",
    ] | None

    # ============================================================
    # PRODUCT / VARIANT CONTEXT
    # ============================================================

    product_id: int | None
    variant_id: int | None

    product_name: str | None
    variant_name: str | None
    sku: str | None

    # ============================================================
    # QUANTITY / ITEM STATE
    # ============================================================

    requested_quantity: int | None
    current_quantity: int | None
    new_quantity: int | None

    cart_item_id: int | None
    wishlist_item_id: int | None

    # ============================================================
    # CART STATE
    # ============================================================

    cart_id: int | None
    cart_items: list[dict[str, Any]]
    cart_total_items: int
    cart_total_amount: float | None

    # ============================================================
    # WISHLIST STATE
    # ============================================================

    wishlist_id: int | None
    wishlist_items: list[dict[str, Any]]

    # ============================================================
    # ACTION STATE
    # ============================================================

    action_type: Literal[
        "add",
        "update",
        "remove",
        "clear",
        "view",
        "none",
    ] | None

    action_target: Literal[
        "cart",
        "wishlist",
        "none",
    ] | None

    action_status: Literal[
        "not_started",
        "preparing",
        "validated",
        "awaiting_confirmation",
        "confirmed",
        "executing",
        "executed",
        "failed",
        "cancelled",
    ]

    # ============================================================
    # PENDING ACTION / CONFIRMATION
    # ============================================================

    pending_action: dict[str, Any] | None

    confirmation_required: bool
    confirmation_received: bool
    confirmation_response: Literal[
        "yes",
        "no",
        "unclear",
        "not_required",
    ] | None

    # ============================================================
    # VALIDATION STATE
    # ============================================================

    validation_status: Literal[
        "not_validated",
        "valid",
        "invalid",
        "requires_revalidation",
    ]

    validation_errors: list[str]

    # ============================================================
    # INVENTORY / AVAILABILITY
    # ============================================================

    stock_available: int | None
    requested_stock: int | None

    is_product_active: bool | None
    is_variant_active: bool | None

    price: float | None
    discount: float | None

    # ============================================================
    # AUTHORIZATION / USER CONTEXT
    # ============================================================

    authenticated: bool
    authorization_status: Literal[
        "not_checked",
        "authorized",
        "unauthorized",
    ]

    # ============================================================
    # TOOL EXECUTION
    # ============================================================

    last_tool: str | None
    last_tool_call_id: str | None

    tool_execution_status: Literal[
        "not_started",
        "running",
        "success",
        "failed",
    ]

    tool_result: dict[str, Any] | None

    # ============================================================
    # TRANSACTION STATE
    # ============================================================

    transaction_started: bool
    transaction_committed: bool
    transaction_rolled_back: bool

    operation_id: str | None

    # ============================================================
    # RESULT STATE
    # ============================================================

    operation_success: bool
    operation_message: str | None

    affected_item_id: int | None

    # ============================================================
    # ERROR HANDLING
    # ============================================================

    error: str | None
    error_code: str | None
    retryable: bool

    # ============================================================
    # CLARIFICATION
    # ============================================================

    clarification_required: bool
    clarification_question: str | None

    # ============================================================
    # WORKFLOW CONTROL
    # ============================================================

    status: Literal[
        "idle",
        "understanding_request",
        "resolving_item",
        "validating",
        "awaiting_confirmation",
        "revalidating",
        "authorizing",
        "executing",
        "verifying",
        "completed",
        "cancelled",
        "failed",
    ]

    next_action: Literal[
        "view_cart",
        "view_wishlist",
        "resolve_product",
        "resolve_variant",
        "validate",
        "ask_confirmation",
        "revalidate",
        "authorize",
        "execute",
        "verify",
        "clarify",
        "respond",
        "end",
    ] | None

    # ============================================================
    # RESPONSE
    # ============================================================

    response: str | None