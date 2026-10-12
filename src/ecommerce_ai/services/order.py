from decimal import Decimal
from typing import Any

from ecommerce_ai.models.order import Order
from ecommerce_ai.repositories.order_repository import OrderRepository
from ecommerce_ai.repositories.shopping_repository import ShoppingRepository


class OrderService:

    def __init__(
        self,
        repository: OrderRepository,
        shopping_repository: ShoppingRepository | None = None,
    ):
        self.repository = repository
        self.shopping_repository = shopping_repository

    # =========================================================
    # HELPERS
    # =========================================================

    def _format_order_summary(self, order: Order) -> dict[str, Any]:
        primary_shipment = (
            order.shipments[0] if order.shipments else None
        )

        items_summary = [
            {
                "product_name": item.product_name_snapshot,
                "quantity": item.quantity,
                "unit_price": str(item.unit_price),
                "variant_id": item.product_variant_id,
            }
            for item in order.items
        ]

        return {
            "order_number": order.order_number,
            "status": order.status,
            "created_at": (
                order.created_at.strftime("%Y-%m-%d %H:%M:%S")
                if order.created_at
                else None
            ),
            "total_amount": str(order.total_amount),
            "item_count": sum(
                item.quantity for item in order.items
            ),
            "items": items_summary,
            "shipment_status": (
                primary_shipment.status
                if primary_shipment
                else "not_shipped"
            ),
            "carrier": (
                primary_shipment.carrier
                if primary_shipment
                else None
            ),
            "tracking_number": (
                primary_shipment.tracking_number
                if primary_shipment
                else None
            ),
            "estimated_delivery": (
                primary_shipment.estimated_delivery_at.strftime(
                    "%Y-%m-%d"
                )
                if primary_shipment
                and primary_shipment.estimated_delivery_at
                else None
            ),
        }

    def _format_order_details(
        self, order: Order
    ) -> dict[str, Any]:
        items_details = [
            {
                "item_id": item.id,
                "product_name": item.product_name_snapshot,
                "variant_id": item.product_variant_id,
                "quantity": item.quantity,
                "unit_price": str(item.unit_price),
                "item_total": str(
                    Decimal(item.unit_price) * item.quantity
                ),
            }
            for item in order.items
        ]

        shipments_details = [
            {
                "carrier": s.carrier,
                "tracking_number": s.tracking_number,
                "status": s.status,
                "shipped_at": (
                    s.shipped_at.strftime("%Y-%m-%d %H:%M:%S")
                    if s.shipped_at
                    else None
                ),
                "estimated_delivery": (
                    s.estimated_delivery_at.strftime("%Y-%m-%d")
                    if s.estimated_delivery_at
                    else None
                ),
                "delivered_at": (
                    s.delivered_at.strftime("%Y-%m-%d %H:%M:%S")
                    if s.delivered_at
                    else None
                ),
            }
            for s in order.shipments
        ]

        payments_details = [
            {
                "payment_method": p.payment_method,
                "amount": str(p.amount),
                "status": p.status,
                "transaction_reference": p.transaction_reference,
            }
            for p in order.payments
        ]

        return {
            "order_id": order.id,
            "order_number": order.order_number,
            "status": order.status,
            "created_at": (
                order.created_at.strftime("%Y-%m-%d %H:%M:%S")
                if order.created_at
                else None
            ),
            "pricing": {
                "subtotal": str(order.subtotal),
                "discount_amount": str(order.discount_amount),
                "shipping_amount": str(order.shipping_amount),
                "tax_amount": str(order.tax_amount),
                "total_amount": str(order.total_amount),
            },
            "shipping_address": order.shipping_address_snapshot,
            "items": items_details,
            "shipments": shipments_details,
            "payments": payments_details,
        }

    # =========================================================
    # LAST ORDER
    # =========================================================

    async def get_last_order(
        self, user_id: int
    ) -> dict[str, Any]:

        order = await self.repository.get_latest_order(
            user_id
        )

        if order is None:
            return {
                "found": False,
                "message": "You have not placed any orders yet.",
            }

        return {
            "found": True,
            "order": self._format_order_details(order),
        }

    # =========================================================
    # ORDER HISTORY
    # =========================================================

    async def get_order_history(
        self,
        user_id: int,
        status: str | None = None,
        limit: int = 5,
    ) -> dict[str, Any]:

        orders = await self.repository.get_orders(
            user_id=user_id,
            status=status,
            limit=limit,
        )

        if not orders:
            filter_msg = (
                f" with status '{status}'" if status else ""
            )
            return {
                "found": False,
                "total_orders": 0,
                "orders": [],
                "message": (
                    f"No past orders found{filter_msg}."
                ),
            }

        return {
            "found": True,
            "total_orders": len(orders),
            "orders": [
                self._format_order_summary(o)
                for o in orders
            ],
        }

    # =========================================================
    # TRACK ORDER
    # =========================================================

    async def track_order(
        self,
        user_id: int,
        order_number: str | None = None,
        tracking_number: str | None = None,
    ) -> dict[str, Any]:

        order: Order | None = None

        if tracking_number:
            order = (
                await self.repository
                .get_order_by_tracking_number(
                    user_id=user_id,
                    tracking_number=tracking_number,
                )
            )
        elif order_number:
            order = (
                await self.repository.get_order_by_number(
                    user_id=user_id,
                    order_number=order_number,
                )
            )
        else:
            order = (
                await self.repository.get_latest_order(
                    user_id
                )
            )

        if order is None:
            ref = (
                tracking_number
                or order_number
                or "your recent order"
            )
            return {
                "found": False,
                "message": (
                    f"Could not find order or tracking "
                    f"information for {ref}."
                ),
            }

        primary_shipment = (
            order.shipments[0] if order.shipments else None
        )
        address = order.shipping_address_snapshot or {}

        items_summary = [
            f"{item.product_name_snapshot} "
            f"(Qty: {item.quantity})"
            for item in order.items
        ]

        tracking_data: dict[str, Any] = {
            "found": True,
            "order_number": order.order_number,
            "order_status": order.status,
            "ordered_at": (
                order.created_at.strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                if order.created_at
                else None
            ),
            "carrier": (
                primary_shipment.carrier
                if primary_shipment
                else "Pending assignment"
            ),
            "tracking_number": (
                primary_shipment.tracking_number
                if primary_shipment
                else "Not yet generated"
            ),
            "shipment_status": (
                primary_shipment.status
                if primary_shipment
                else "processing"
            ),
            "estimated_delivery": (
                primary_shipment.estimated_delivery_at
                .strftime("%Y-%m-%d")
                if primary_shipment
                and primary_shipment.estimated_delivery_at
                else None
            ),
            "delivered_at": (
                primary_shipment.delivered_at.strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                if primary_shipment
                and primary_shipment.delivered_at
                else None
            ),
            "destination": {
                "recipient_name": address.get(
                    "recipient_name"
                ),
                "city": address.get("city"),
                "state": address.get("state"),
                "postal_code": address.get("postal_code"),
            },
            "items": items_summary,
            "total_amount": str(order.total_amount),
        }

        if order.status.lower() == "delivered":
            delivery_date = (
                tracking_data["delivered_at"] or "recently"
            )
            tracking_data["status_summary"] = (
                f"Order {order.order_number} has been "
                f"delivered on {delivery_date} via "
                f"{tracking_data['carrier']} "
                f"(Tracking: "
                f"{tracking_data['tracking_number']})."
            )
        elif order.status.lower() == "shipped" or (
            primary_shipment
            and primary_shipment.status == "in_transit"
        ):
            est = (
                tracking_data["estimated_delivery"]
                or "soon"
            )
            tracking_data["status_summary"] = (
                f"Order {order.order_number} is in transit "
                f"with {tracking_data['carrier']} "
                f"(Tracking: "
                f"{tracking_data['tracking_number']}). "
                f"Estimated delivery is {est}."
            )
        elif order.status.lower() == "cancelled":
            tracking_data["status_summary"] = (
                f"Order {order.order_number} has been "
                f"cancelled."
            )
        else:
            tracking_data["status_summary"] = (
                f"Order {order.order_number} is currently "
                f"being processed and prepared for "
                f"shipping."
            )

        return tracking_data

    # =========================================================
    # ORDER DETAILS
    # =========================================================

    async def get_order_details(
        self,
        user_id: int,
        order_number: str,
    ) -> dict[str, Any]:

        order = (
            await self.repository.get_order_by_number(
                user_id=user_id,
                order_number=order_number,
            )
        )

        if order is None:
            return {
                "found": False,
                "message": (
                    f"Order with number "
                    f"'{order_number}' was not found."
                ),
            }

        return {
            "found": True,
            "order": self._format_order_details(order),
        }

    # =========================================================
    # COMPARE ORDER WITH CART
    # =========================================================

    async def compare_order_with_cart(
        self,
        user_id: int,
        order_number: str | None = None,
    ) -> dict[str, Any]:

        if order_number:
            order = (
                await self.repository.get_order_by_number(
                    user_id, order_number
                )
            )
        else:
            order = (
                await self.repository.get_latest_order(
                    user_id
                )
            )

        if order is None:
            ref = (
                f"'{order_number}'"
                if order_number
                else "any past orders"
            )
            return {
                "success": False,
                "message": (
                    f"Could not find {ref} to compare "
                    f"with the cart."
                ),
            }

        cart_rows = []
        if self.shopping_repository is not None:
            cart_rows = (
                await self.shopping_repository.get_cart(
                    user_id
                )
            )

        cart_by_variant: dict[int, dict[str, Any]] = {}
        cart_total = Decimal("0.00")

        for cart_item, product, variant in cart_rows:
            effective_price = (
                variant.price - variant.discount
            )
            line_total = (
                effective_price * cart_item.quantity
            )
            cart_total += line_total
            cart_by_variant[variant.id] = {
                "product_name": product.name,
                "variant_name": variant.name,
                "variant_id": variant.id,
                "cart_quantity": cart_item.quantity,
                "current_unit_price": str(effective_price),
                "cart_line_total": str(line_total),
            }

        order_by_variant: dict[int, dict[str, Any]] = {}
        for item in order.items:
            order_by_variant[item.product_variant_id] = {
                "product_name": item.product_name_snapshot,
                "variant_id": item.product_variant_id,
                "order_quantity": item.quantity,
                "ordered_unit_price": str(item.unit_price),
                "order_line_total": str(
                    Decimal(item.unit_price) * item.quantity
                ),
            }

        items_in_both = []
        items_only_in_order = []
        items_only_in_cart = []

        all_variant_ids = (
            set(order_by_variant.keys())
            | set(cart_by_variant.keys())
        )

        for vid in all_variant_ids:
            in_order = vid in order_by_variant
            in_cart = vid in cart_by_variant

            if in_order and in_cart:
                o_item = order_by_variant[vid]
                c_item = cart_by_variant[vid]
                items_in_both.append({
                    "product_name": o_item["product_name"],
                    "variant_id": vid,
                    "order_quantity": (
                        o_item["order_quantity"]
                    ),
                    "cart_quantity": (
                        c_item["cart_quantity"]
                    ),
                    "quantity_difference": (
                        c_item["cart_quantity"]
                        - o_item["order_quantity"]
                    ),
                    "ordered_unit_price": (
                        o_item["ordered_unit_price"]
                    ),
                    "current_cart_unit_price": (
                        c_item["current_unit_price"]
                    ),
                })
            elif in_order:
                o_item = order_by_variant[vid]
                items_only_in_order.append({
                    "product_name": o_item["product_name"],
                    "variant_id": vid,
                    "order_quantity": (
                        o_item["order_quantity"]
                    ),
                    "ordered_unit_price": (
                        o_item["ordered_unit_price"]
                    ),
                })
            elif in_cart:
                c_item = cart_by_variant[vid]
                items_only_in_cart.append({
                    "product_name": c_item["product_name"],
                    "variant_id": vid,
                    "cart_quantity": (
                        c_item["cart_quantity"]
                    ),
                    "current_unit_price": (
                        c_item["current_unit_price"]
                    ),
                })

        return {
            "success": True,
            "order_number": order.order_number,
            "order_date": (
                order.created_at.strftime("%Y-%m-%d")
                if order.created_at
                else None
            ),
            "order_total": str(order.total_amount),
            "cart_total": str(cart_total),
            "total_difference": str(
                cart_total - order.total_amount
            ),
            "items_in_both": items_in_both,
            "items_only_in_order": items_only_in_order,
            "items_only_in_cart": items_only_in_cart,
            "summary": {
                "both_count": len(items_in_both),
                "missing_from_cart_count": len(
                    items_only_in_order
                ),
                "new_in_cart_count": len(
                    items_only_in_cart
                ),
            },
        }

    # =========================================================
    # SEARCH PAST ORDERS
    # =========================================================

    async def search_past_orders(
        self,
        user_id: int,
        product_name: str,
    ) -> dict[str, Any]:

        orders = (
            await self.repository
            .search_orders_by_product_name(
                user_id=user_id,
                query=product_name,
            )
        )

        if not orders:
            return {
                "found": False,
                "message": (
                    f"No past orders found containing "
                    f"'{product_name}'."
                ),
                "orders": [],
            }

        return {
            "found": True,
            "query": product_name,
            "matching_orders_count": len(orders),
            "orders": [
                self._format_order_summary(o)
                for o in orders
            ],
        }

    # =========================================================
    # CANCEL ORDER
    # =========================================================

    async def cancel_order(
        self,
        user_id: int,
        order_number: str,
    ) -> dict[str, Any]:

        success, message, order = (
            await self.repository.cancel_order(
                user_id=user_id,
                order_number=order_number,
            )
        )

        return {
            "success": success,
            "message": message,
            "order_number": (
                order.order_number
                if order
                else order_number
            ),
            "new_status": (
                order.status if order else None
            ),
        }

    # =========================================================
    # HUMAN-IN-THE-LOOP: PREPARE CHECKOUT ORDER (PREVIEW)
    # =========================================================

    async def prepare_checkout_order(
        self,
        user_id: int,
        address_id: int | None = None,
        payment_method: str = "Cash on Delivery",
    ) -> dict[str, Any]:
        """
        Step 1 of Human-in-the-Loop Checkout:
        Inspects cart, validates stock, calculates itemized totals,
        retrieves shipping address, and returns an order preview.
        Explicitly asks the user to confirm before placing.
        """

        if self.shopping_repository is None:
            return {
                "success": False,
                "status": "error",
                "message": "Shopping repository is not configured.",
            }

        cart_rows = await self.shopping_repository.get_cart(user_id)
        if not cart_rows:
            return {
                "success": False,
                "status": "cart_empty",
                "message": "Your cart is empty. Please add items to your cart before proceeding to checkout.",
            }

        # Validate stock
        items_preview = []
        subtotal = Decimal("0.00")
        total_discount = Decimal("0.00")

        for cart_item, product, variant in cart_rows:
            if not variant.is_active or variant.stock_quantity < cart_item.quantity:
                return {
                    "success": False,
                    "status": "stock_error",
                    "message": f"Cannot checkout: '{variant.name}' has only {variant.stock_quantity} unit(s) available, but your cart has {cart_item.quantity}.",
                }

            item_price = variant.price * cart_item.quantity
            item_discount = variant.discount * cart_item.quantity
            effective_price = variant.price - variant.discount
            line_total = effective_price * cart_item.quantity

            subtotal += item_price
            total_discount += item_discount

            items_preview.append({
                "product_name": product.name,
                "variant_name": variant.name,
                "quantity": cart_item.quantity,
                "original_unit_price": str(variant.price),
                "unit_discount": str(variant.discount),
                "effective_unit_price": str(effective_price),
                "line_total": str(line_total),
            })

        # Shipping and tax calculations
        net_subtotal = max(Decimal("0.00"), subtotal - total_discount)
        shipping_fee = Decimal("0.00") if net_subtotal >= Decimal("500.00") else Decimal("50.00")
        tax = (net_subtotal * Decimal("0.18")).quantize(Decimal("0.01"))
        total_amount = net_subtotal + shipping_fee + tax

        # Shipping address
        address = None
        if address_id:
            address = await self.repository.get_address_by_id(user_id, address_id)
        else:
            address = await self.repository.get_default_address(user_id)

        if address is None:
            return {
                "success": False,
                "status": "no_address",
                "message": "No delivery address found. Please add a shipping address before checkout.",
            }

        address_str = f"{address.recipient_name}, {address.address_line1}, {address.city}, {address.state} - {address.postal_code} (Phone: {address.phone or 'N/A'})"

        return {
            "success": True,
            "status": "awaiting_confirmation",
            "items_count": len(items_preview),
            "items": items_preview,
            "pricing": {
                "subtotal": str(subtotal),
                "discount": str(total_discount),
                "net_subtotal": str(net_subtotal),
                "shipping_fee": str(shipping_fee),
                "tax_gst": str(tax),
                "total_amount": str(total_amount),
            },
            "delivery_address": address_str,
            "address_id": address.id,
            "payment_method": payment_method,
            "requires_confirmation": True,
            "confirmation_instructions": (
                "IMPORTANT: Review the order breakdown above with the user. "
                "Explicitly ask the user: 'Would you like me to proceed and place this order?' "
                "Do NOT call place_order_from_cart until the user explicitly says yes or confirms."
            ),
        }

    # =========================================================
    # HUMAN-IN-THE-LOOP: PLACE ORDER (AFTER CONFIRMATION)
    # =========================================================

    async def place_order_from_cart(
        self,
        user_id: int,
        confirmed: bool = False,
        payment_method: str = "cod",
        address_id: int | None = None,
    ) -> dict[str, Any]:
        """
        Step 2 of Human-in-the-Loop Checkout:
        Guarded execution tool. Fails if confirmed=False.
        """

        if not confirmed:
            return {
                "success": False,
                "status": "confirmation_required",
                "message": (
                    "Order placement was blocked because explicit user confirmation was not provided. "
                    "You must ask the user for confirmation (e.g. 'Would you like to confirm this order?') "
                    "and only proceed when confirmed=True."
                ),
            }

        success, message, order = await self.repository.create_order_from_cart(
            user_id=user_id,
            address_id=address_id,
            payment_method=payment_method,
        )

        if not success or order is None:
            return {
                "success": False,
                "status": "failed",
                "message": message,
            }

        primary_shipment = order.shipments[0] if order.shipments else None
        return {
            "success": True,
            "status": "placed",
            "order_number": order.order_number,
            "total_amount": str(order.total_amount),
            "tracking_number": primary_shipment.tracking_number if primary_shipment else None,
            "carrier": primary_shipment.carrier if primary_shipment else "BlueDart",
            "estimated_delivery": (
                primary_shipment.estimated_delivery_at.strftime("%Y-%m-%d")
                if primary_shipment and primary_shipment.estimated_delivery_at
                else "In 3-4 business days"
            ),
            "shipping_address": order.shipping_address_snapshot,
            "message": f"Order {order.order_number} has been placed successfully!",
        }

    # =========================================================
    # ADDRESSES
    # =========================================================

    async def get_user_addresses(self, user_id: int) -> dict[str, Any]:
        addresses = await self.repository.get_user_addresses(user_id)
        if not addresses:
            return {
                "found": False,
                "addresses": [],
                "message": "No saved shipping addresses found.",
            }

        return {
            "found": True,
            "total": len(addresses),
            "addresses": [
                {
                    "address_id": a.id,
                    "recipient_name": a.recipient_name,
                    "address": f"{a.address_line1}, {a.city}, {a.state} - {a.postal_code}",
                    "phone": a.phone,
                    "is_default": a.is_default,
                }
                for a in addresses
            ],
        }

    # =========================================================
    # REORDER PAST ORDER
    # =========================================================

    async def reorder_past_order(
        self,
        user_id: int,
        order_number: str | None = None,
    ) -> dict[str, Any]:

        if not order_number:
            latest = await self.repository.get_latest_order(user_id)
            if latest is None:
                return {
                    "success": False,
                    "message": "No previous orders found to reorder.",
                }
            order_number = latest.order_number

        success, message, items = await self.repository.reorder_to_cart(
            user_id=user_id,
            order_number=order_number,
        )

        return {
            "success": success,
            "order_number": order_number,
            "message": message,
            "reordered_items": items,
        }
