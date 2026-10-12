from typing import Literal
import json

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from pydantic import BaseModel, Field


# ============================================================
# Intent Definition
# ============================================================

Intent = Literal[
    "product",
    "shopping",
    "order",
    "support",
    "unknown",
]


# ============================================================
# Structured Classification Output
# ============================================================

class IntentClassification(BaseModel):
    """
    Structured output returned by the intent classifier.

    A single user request may contain multiple intents.

    Example:

    {
        "intents": ["product", "shopping", "order"],
        "confidence": 0.97
    }
    """

    intents: list[Intent] = Field(
        min_length=1,
        description=(
            "All intents detected in the user's request."
        ),
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description=(
            "Confidence in the overall classification."
        ),
    )


# ============================================================
# Intent Classification Prompt
# ============================================================

INTENT_CLASSIFICATION_PROMPT = """
You are the intent classifier for an e-commerce application.

Your job is to identify ALL intents present in the user's request.

A single user request can contain multiple intents.

Available intents:

product:
The user wants to discover, search, browse, compare,
or get information about products.

shopping:
The user wants to manage their shopping cart or wishlist
(such as adding items, removing items, updating quantities,
viewing the cart, or wishlist operations).

order:
The user wants to place an order, checkout their cart,
buy the items in their cart, or query about existing orders,
shipments, delivery, or tracking.

support:
The user has a problem, complaint, damaged product,
return/refund issue, or needs customer support.

unknown:
The request does not clearly belong to any category.

IMPORTANT RULES
----------------

1. A request can contain MULTIPLE intents.

2. Return ALL applicable intents.

3. Do NOT stop after identifying the first intent.

4. Do NOT classify based only on product entities.

   For example:
   "laptop", "phone", "TV", etc.
   do NOT automatically mean "product".

5. Focus on what the user wants to DO.

6. Preserve the logical order of the user's requested
   actions when possible.

7. Do not include "unknown" together with valid intents.

8. Use "unknown" only when no valid intent can be identified.

Examples:

User:
"Show me laptops under 70000"

Output:
{
    "intents": ["product"],
    "confidence": 0.98
}

User:
"Add this laptop to my cart"

Output:
{
    "intents": ["shopping"],
    "confidence": 0.99
}

User:
"Find me a gaming laptop under 70000 and add the first one to my cart"

Output:
{
    "intents": ["product", "shopping"],
    "confidence": 0.97
}

User:
"Find me a Lenovo laptop under 70000, add the first one to my cart, and show me my latest order status"

Output:
{
    "intents": ["product", "shopping", "order"],
    "confidence": 0.97
}

User:
"Show me laptops and tell me where my latest order is"

Output:
{
    "intents": ["product", "order"],
    "confidence": 0.97
}

User:
"My laptop arrived damaged and I want a refund"

Output:
{
    "intents": ["support"],
    "confidence": 0.96
}

User:
"I need help"

Output:
{
    "intents": ["unknown"],
    "confidence": 0.60
}

IMPORTANT:
Return ONLY valid JSON.

The JSON must have exactly these fields:

{
    "intents": ["product", "shopping", "order", "support", "unknown"],
    "confidence": 0.0
}

Do not use markdown.
Do not use explanations.
Do not return YAML.
Do not return text outside the JSON.
"""


# ============================================================
# Intent Classifier
# ============================================================

class IntentClassifier:

    def __init__(self):

        self.model = ChatOllama(
            model="gpt-oss:120b-cloud",
            temperature=0,
        )

    # ========================================================
    # Rule-Based Classification
    # ========================================================

    def rule_based_classification(
        self,
        text: str,
    ) -> IntentClassification | None:

        text = text.lower().strip()

        detected_intents: list[Intent] = []

        # ====================================================
        # SHOPPING
        # ====================================================

        shopping_phrases = [
            "add to cart",
            "add this to cart",
            "add it to cart",
            "add that to cart",
            "remove from cart",
            "remove this from cart",
            "remove it from cart",
            "show my cart",
            "view my cart",
            "checkout",
            "check out",
            "empty my cart",
            "clear my cart",
            "add to wishlist",
            "remove from wishlist",
            "view my wishlist",
            "show my wishlist",
            "cart",
            "basket",
            "wishlist",
            "wish list",
            "shopping bag",
            "shopping basket",
        ]

        if any(
            phrase in text
            for phrase in shopping_phrases
        ):
            detected_intents.append("shopping")

        # ====================================================
        # ORDER
        # ====================================================

        order_phrases = [
            "track my order",
            "track order",
            "where is my order",
            "where's my order",
            "order status",
            "shipment status",
            "delivery status",
            "track my shipment",
            "track shipment",
            "latest order",
            "latest order status",
            "my recent order",
            "my recent order status",
            "last order",
            "order history",
            "past order",
            "past orders",
            "my orders",
            "compare order",
            "compare my order",
            "cancel order",
            "order details",
            "place this order",
            "place order",
            "place my order",
            "place the order",
            "order the items in my cart",
            "order my cart",
            "checkout order",
        ]

        if any(
            phrase in text
            for phrase in order_phrases
        ):
            detected_intents.append("order")

        # ====================================================
        # SUPPORT
        # ====================================================

        support_phrases = [
            "product is damaged",
            "product arrived damaged",
            "received damaged",
            "my product is broken",
            "product is broken",
            "item is damaged",
            "item arrived damaged",
            "i have a complaint",
            "i want to complain",
            "need customer support",
            "need support",
            "want a refund",
            "need a refund",
            "return this product",
            "return this item",
        ]

        if any(
            phrase in text
            for phrase in support_phrases
        ):
            detected_intents.append("support")

        # ====================================================
        # PRODUCT DISCOVERY
        # ====================================================

        product_phrases = [
            "list me the products",
            "list me products",
            "list all products",
            "list products",
            "show all products",
            "show me all products",
            "show me the products",
            "show me products",
            "show products",
            "all products",
            "available products",
            "show me laptops",
            "show me phones",
            "show me tvs",
            "show me televisions",
            "find products",
            "find laptops",
            "find phones",
            "find tvs",
            "find televisions",
            "search for laptops",
            "search for phones",
            "search for tvs",
            "search for products",
            "look for laptops",
            "look for phones",
            "browse laptops",
            "browse phones",
            "compare products",
            "compare laptops",
            "compare phones",
            "compare tvs",
        ]

        if any(
            phrase in text
            for phrase in product_phrases
        ):
            detected_intents.append("product")

        # ====================================================
        # Remove duplicates while preserving order
        # ====================================================

        detected_intents = list(
            dict.fromkeys(detected_intents)
        )

        # ====================================================
        # Exactly ONE intent detected
        # ====================================================

        if len(detected_intents) == 1:

            return IntentClassification(
                intents=detected_intents,
                confidence=0.99,
            )

        # ====================================================
        # Multiple intents detected
        # ====================================================
        #
        # Do NOT immediately trust the rules.
        #
        # Let the LLM inspect the complete sentence because
        # the rule system may have missed another intent.
        #
        # Example:
        #
        # "Find me a laptop and add it to my cart"
        #
        # Rules might detect:
        #
        # ["shopping"]
        #
        # while the actual intents are:
        #
        # ["product", "shopping"]
        #
        # ====================================================

        if len(detected_intents) > 1:

            return None

        # ====================================================
        # No rule matched
        # ====================================================

        return None

    # ========================================================
    # Main Classification Method
    # ========================================================

    async def classify(
        self,
        text: str,
    ) -> IntentClassification:

        # ====================================================
        # STEP 1: Rule-Based Classification
        # ====================================================

        rule_result = self.rule_based_classification(
            text
        )

        if rule_result is not None:

            print(
                f"[INTENT] Rule-based → "
                f"{rule_result.intents} "
                f"(confidence={rule_result.confidence})"
            )

            return rule_result

        # ====================================================
        # STEP 2: LLM Classification
        # ====================================================

        print(
            "[INTENT] LLM classification"
        )

        response = await self.model.ainvoke(
            [
                SystemMessage(
                    content=INTENT_CLASSIFICATION_PROMPT
                ),
                HumanMessage(
                    content=text
                ),
            ]
        )

        raw_output = response.content

        print(
            "[INTENT] Raw LLM output:\n"
            f"{raw_output}"
        )

        # ====================================================
        # STEP 3: Parse JSON
        # ====================================================

        try:

            data = json.loads(
                raw_output.strip()
            )

            result = IntentClassification.model_validate(
                data
            )

        except (
            json.JSONDecodeError,
            ValueError,
            TypeError,
        ) as exc:

            print(
                "[INTENT] Failed to parse LLM output: "
                f"{exc}"
            )

            return IntentClassification(
                intents=["unknown"],
                confidence=0.0,
            )

        # ====================================================
        # STEP 4: Normalize Intents
        # ====================================================

        result.intents = list(
            dict.fromkeys(
                result.intents
            )
        )

        # ----------------------------------------------------
        # unknown should never coexist with valid intents
        # ----------------------------------------------------

        if (
            len(result.intents) > 1
            and "unknown" in result.intents
        ):

            result.intents = [
                intent
                for intent in result.intents
                if intent != "unknown"
            ]

        # Safety fallback
        if not result.intents:

            result.intents = ["unknown"]

        # ====================================================
        # STEP 5: Logging
        # ====================================================

        print(
            "[INTENT] LLM → "
            f"{result.intents} "
            f"(confidence={result.confidence})"
        )

        # ====================================================
        # STEP 6: Confidence Threshold
        # ====================================================

        if result.confidence < 0.70:

            print(
                "[INTENT] Low confidence → unknown"
            )

            return IntentClassification(
                intents=["unknown"],
                confidence=result.confidence,
            )

        # ====================================================
        # STEP 7: Return Final Result
        # ====================================================

        return result