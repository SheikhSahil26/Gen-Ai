from typing import Any

from langgraph.graph import MessagesState
from typing_extensions import NotRequired


class SupportAgentState(MessagesState, total=False):
    """
    State used by the Support Agent subgraph.

    The state contains:
    - the user's support request
    - support-query analysis
    - product/order context
    - retrieved knowledge
    - retrieval validation
    - generated answer
    - escalation information
    - errors
    """

    # ============================================================
    # REQUEST
    # ============================================================

    original_query: NotRequired[str]

    current_query: NotRequired[str]

    # ============================================================
    # SUPPORT QUERY ANALYSIS
    # ============================================================

    support_intent: NotRequired[str]

    search_query: NotRequired[str]

    requires_order_context: NotRequired[bool]

    requires_product_context: NotRequired[bool]

    # ============================================================
    # LIVE APPLICATION CONTEXT
    # ============================================================

    active_product_context: NotRequired[
        dict[str, Any] | None
    ]

    active_order_context: NotRequired[
        dict[str, Any] | None
    ]

    # ============================================================
    # RAG
    # ============================================================

    retrieved_documents: NotRequired[
        list[dict[str, Any]]
    ]

    relevant_documents: NotRequired[
        list[dict[str, Any]]
    ]

    retrieval_confidence: NotRequired[float]

    # ============================================================
    # RESPONSE
    # ============================================================

    grounded_answer: NotRequired[str | None]

    citations: NotRequired[
        list[dict[str, Any]]
    ]

    # ============================================================
    # ESCALATION
    # ============================================================

    can_resolve: NotRequired[bool]

    requires_escalation: NotRequired[bool]

    escalation_reason: NotRequired[str | None]

    # ============================================================
    # ERROR HANDLING
    # ============================================================

    error: NotRequired[str | None]

    error_code: NotRequired[str | None]

    retryable: NotRequired[bool]