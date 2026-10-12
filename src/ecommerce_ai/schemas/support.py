from typing import Literal

from pydantic import BaseModel, Field,AliasChoices


SupportIntent = Literal[
    "product_issue",
    "delivery_issue",
    "return_question",
    "refund_question",
    "cancellation_question",
    "payment_issue",
    "warranty_question",
    "policy_question",
    "troubleshooting",
    "general_support",
]


class SupportQueryAnalysis(BaseModel):
    """
    Structured analysis of a customer support request.
    """

    support_intent: SupportIntent = Field(
         validation_alias=AliasChoices(
            "support_intent",
            "intent",
        ),
        description="The primary support issue described by the user."
    )

    search_query: str = Field(
        min_length=1,
        description=(
            "A concise semantic search query optimized "
            "for the support knowledge base."
        ),
    )

    requires_order_context: bool = Field(
        description=(
            "Whether resolving the request requires "
            "information about the user's actual order."
        )
    )

    requires_product_context: bool = Field(
        description=(
            "Whether resolving the request requires "
            "information about a specific product."
        )
    )


class RetrievalValidation(BaseModel):
    """
    Determines whether retrieved support knowledge is
    sufficient and relevant for answering the user's question.
    """

    relevant: bool

    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )

    reason: str = Field(
        min_length=1,
    )


class SupportAnswerValidation(BaseModel):
    """
    Validates whether the generated answer is grounded
    in the available information.
    """

    grounded: bool

    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )

    requires_escalation: bool

    reason: str = Field(
        min_length=1,
    )