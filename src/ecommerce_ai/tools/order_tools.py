from typing import Annotated

from langchain_core.tools import tool
from pydantic import Field

from ecommerce_ai.auth.user_context import get_user_id
from ecommerce_ai.repositories.order_repository import (
    OrderRepository,
)
from ecommerce_ai.repositories.shopping_repository import (
    ShoppingRepository,
)
from ecommerce_ai.services.order import OrderService


def create_order_tools(
    repository: OrderRepository,
    shopping_repository: ShoppingRepository | None = None,
):

    service = OrderService(
        repository=repository,
        shopping_repository=shopping_repository,
    )

    # =========================================================
    # Track Order / Where is my order
    # =========================================================

    @tool
    async def track_order(
        order_number: Annotated[
            str | None,
            Field(
                default=None,
                description=(
                    "Optional order number to track "
                    "(e.g. 'ORD-2026-0001'). "
                    "If omitted, tracks the user's "
                    "latest order."
                ),
            ),
        ] = None,
        tracking_number: Annotated[
            str | None,
            Field(
                default=None,
                description=(
                    "Optional shipment tracking number "
                    "(e.g. 'TRK-100001')."
                ),
            ),
        ] = None,
    ):
        """
        Track the status and shipping progress of an order.

        Use this tool when the user asks:
        - "Where is my order?"
        - "Track my order"
        - "When will my package arrive?"
        - "Has my order shipped or delivered?"
        - "Track package TRK-100001"
        - "Status of order ORD-2026-0001"

        If the user does not specify an order number or
        tracking number, omit both arguments and this tool
        will automatically track their most recent order.
        """

        user_id = get_user_id()

        return await service.track_order(
            user_id=user_id,
            order_number=order_number,
            tracking_number=tracking_number,
        )

    # =========================================================
    # Last Order
    # =========================================================

    @tool
    async def get_last_order():
        """
        Get the most recent order placed by the user.

        Use this tool when the user asks:
        - "What was my last order?"
        - "Show my latest order"
        - "Find my last order placed"
        - "What did I order recently?"
        """

        user_id = get_user_id()

        return await service.get_last_order(
            user_id=user_id
        )

    # =========================================================
    # Order History
    # =========================================================

    @tool
    async def get_order_history(
        status: Annotated[
            str | None,
            Field(
                default=None,
                description=(
                    "Optional filter by order status: "
                    "'delivered', 'shipped', 'pending', "
                    "'cancelled'."
                ),
            ),
        ] = None,
        limit: Annotated[
            int,
            Field(
                default=5,
                ge=1,
                le=20,
                description=(
                    "Maximum number of orders to return."
                ),
            ),
        ] = 5,
    ):
        """
        View past order history for the current user.

        Use this tool when the user asks:
        - "Show my order history"
        - "List my past orders"
        - "Show my delivered orders"
        - "All orders I placed"
        """

        user_id = get_user_id()

        return await service.get_order_history(
            user_id=user_id,
            status=status,
            limit=limit,
        )

    # =========================================================
    # Order Details
    # =========================================================

    @tool
    async def get_order_details(
        order_number: Annotated[
            str,
            Field(
                description=(
                    "Exact order number identifier "
                    "(e.g. 'ORD-2026-0001')."
                ),
            ),
        ],
    ):
        """
        Get detailed information for a specific order.

        Use this tool when the user asks about:
        - Details, receipt, or invoice of a specific order
        - Line items, quantities, and prices for an order
        - Payment method and status of an order
        - Shipping address associated with an order
        """

        user_id = get_user_id()

        return await service.get_order_details(
            user_id=user_id,
            order_number=order_number,
        )

    # =========================================================
    # Compare Order With Cart
    # =========================================================

    @tool
    async def compare_order_with_cart(
        order_number: Annotated[
            str | None,
            Field(
                default=None,
                description=(
                    "Optional order number to compare. "
                    "If omitted, the user's latest order "
                    "is compared."
                ),
            ),
        ] = None,
    ):
        """
        Compare an order with the user's current shopping
        cart.

        Use this tool when the user asks:
        - "Compare my last order with my cart"
        - "What is in my cart compared to my previous order?"
        - "Did I put everything from my last order into cart?"
        - "Compare order ORD-2026-0001 with my cart"
        """

        user_id = get_user_id()

        return await service.compare_order_with_cart(
            user_id=user_id,
            order_number=order_number,
        )

    # =========================================================
    # Search Past Orders
    # =========================================================

    @tool
    async def search_past_orders(
        product_name: Annotated[
            str,
            Field(
                description=(
                    "Product name or keyword to search "
                    "for in past orders."
                ),
            ),
        ],
    ):
        """
        Search user's past orders for a specific product.

        Use this tool when the user asks:
        - "Did I buy a laptop before?"
        - "When did I order Sony headphones?"
        - "Find my order with Galaxy S24"
        """

        user_id = get_user_id()

        return await service.search_past_orders(
            user_id=user_id,
            product_name=product_name,
        )

    # =========================================================
    # Cancel Order
    # =========================================================

    @tool
    async def cancel_order(
        order_number: Annotated[
            str,
            Field(
                description=(
                    "Order number of the order to cancel "
                    "(e.g. 'ORD-2026-0001')."
                ),
            ),
        ],
    ):
        """
        Request cancellation of an order.

        Use this tool when the user asks to cancel an order.
        Orders that have already shipped or been delivered
        cannot be cancelled directly.
        """

        user_id = get_user_id()

        return await service.cancel_order(
            user_id=user_id,
            order_number=order_number,
        )

    # =========================================================
    # HUMAN-IN-THE-LOOP: PREPARE CHECKOUT ORDER
    # =========================================================

    @tool
    async def prepare_checkout_order(
        payment_method: Annotated[
            str,
            Field(
                default="Cash on Delivery",
                description="Payment method: 'Cash on Delivery', 'UPI', 'Credit Card'.",
            ),
        ] = "Cash on Delivery",
        address_id: Annotated[
            int | None,
            Field(
                default=None,
                description="Optional shipping address ID. If omitted, the default address is used.",
            ),
        ] = None,
    ):
        """
        STEP 1 of Human-in-the-Loop Checkout:
        Inspects the cart, checks stock availability, calculates subtotal,
        discounts, shipping fee, tax, and total price, and retrieves the
        delivery address.

        Use this tool to generate an order preview BEFORE the user has confirmed.
        Use when the user starts checkout: "I want to place this order", "Checkout my cart".
        Do NOT call this tool if an order preview was already presented and the user is now
        replying to confirm it (e.g. "Yes", "Confirm", "Proceed"). For confirmations,
        use place_order_from_cart(confirmed=True).
        """

        user_id = get_user_id()

        return await service.prepare_checkout_order(
            user_id=user_id,
            address_id=address_id,
            payment_method=payment_method,
        )

    # =========================================================
    # HUMAN-IN-THE-LOOP: PLACE ORDER (CONFIRMED)
    # =========================================================

    @tool
    async def place_order_from_cart(
        confirmed: Annotated[
            bool,
            Field(
                description=(
                    "Set to True ONLY when the human user has explicitly confirmed "
                    "that they want to place the order (e.g. said 'Yes', 'Confirm', "
                    "'Place it', 'Proceed'). If the user has not confirmed yet, do NOT "
                    "set to True."
                ),
            ),
        ],
        payment_method: Annotated[
            str,
            Field(
                default="cod",
                description="Payment method: 'cod' (Cash on Delivery), 'upi', 'card'.",
            ),
        ] = "cod",
        address_id: Annotated[
            int | None,
            Field(
                default=None,
                description="Optional shipping address ID.",
            ),
        ] = None,
    ):
        """
        STEP 2 of Human-in-the-Loop Checkout:
        Places the order for the items in the user's cart, deducts inventory,
        creates the shipment tracking number, records payment, and clears the cart.

        CRITICAL SAFETY RULE:
        Only call this tool with confirmed=True AFTER the user has explicitly confirmed
        the order preview that was shown in prepare_checkout_order.
        """

        user_id = get_user_id()

        return await service.place_order_from_cart(
            user_id=user_id,
            confirmed=confirmed,
            payment_method=payment_method,
            address_id=address_id,
        )

    # =========================================================
    # Addresses
    # =========================================================

    @tool
    async def get_user_addresses():
        """
        Get the list of saved shipping addresses for the user.
        Use when user asks "What is my shipping address?" or wants to choose
        where to deliver.
        """

        user_id = get_user_id()

        return await service.get_user_addresses(
            user_id=user_id,
        )

    # =========================================================
    # Reorder
    # =========================================================

    @tool
    async def reorder_past_order(
        order_number: Annotated[
            str | None,
            Field(
                default=None,
                description="Order number to reorder. If omitted, reorders items from the latest order.",
            ),
        ] = None,
    ):
        """
        Add items from a past order back into the shopping cart for easy re-ordering.
        Use when user asks: "Reorder my last order", "Buy the same items again".
        """

        user_id = get_user_id()

        return await service.reorder_past_order(
            user_id=user_id,
            order_number=order_number,
        )

    return [
        track_order,
        get_last_order,
        get_order_history,
        get_order_details,
        compare_order_with_cart,
        search_past_orders,
        cancel_order,
        prepare_checkout_order,
        place_order_from_cart,
        get_user_addresses,
        reorder_past_order,
    ]
