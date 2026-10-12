from datetime import datetime, timedelta, timezone
from decimal import Decimal
import random

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ecommerce_ai.models.order import (
    Order,
    OrderItem,
    Payment,
    Shipment,
    ShipmentItem,
)
from ecommerce_ai.models.product import Product, ProductVariant
from ecommerce_ai.models.shopping import Address, Cart, CartItem


class OrderRepository:

    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

    # =========================================================
    # GET ORDERS / HISTORY
    # =========================================================

    async def get_orders(
        self,
        user_id: int,
        status: str | None = None,
        limit: int = 10,
    ) -> list[Order]:

        stmt = (
            select(Order)
            .where(Order.user_id == user_id)
            .options(
                selectinload(Order.items).selectinload(OrderItem.product_variant),
                selectinload(Order.shipments).selectinload(Shipment.items),
                selectinload(Order.payments),
            )
            .order_by(Order.created_at.desc())
        )

        if status:
            stmt = stmt.where(Order.status.ilike(status.strip()))

        if limit:
            stmt = stmt.limit(limit)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    # =========================================================
    # GET LATEST ORDER
    # =========================================================

    async def get_latest_order(
        self,
        user_id: int,
    ) -> Order | None:

        stmt = (
            select(Order)
            .where(Order.user_id == user_id)
            .options(
                selectinload(Order.items).selectinload(OrderItem.product_variant),
                selectinload(Order.shipments).selectinload(Shipment.items),
                selectinload(Order.payments),
            )
            .order_by(Order.created_at.desc())
            .limit(1)
        )

        result = await self.session.execute(stmt)
        return result.scalars().first()

    # =========================================================
    # GET ORDER BY NUMBER
    # =========================================================

    async def get_order_by_number(
        self,
        user_id: int,
        order_number: str,
    ) -> Order | None:

        stmt = (
            select(Order)
            .where(
                Order.user_id == user_id,
                Order.order_number.ilike(order_number.strip()),
            )
            .options(
                selectinload(Order.items).selectinload(OrderItem.product_variant),
                selectinload(Order.shipments).selectinload(Shipment.items),
                selectinload(Order.payments),
            )
            .limit(1)
        )

        result = await self.session.execute(stmt)
        return result.scalars().first()

    # =========================================================
    # GET ORDER BY TRACKING NUMBER
    # =========================================================

    async def get_order_by_tracking_number(
        self,
        user_id: int,
        tracking_number: str,
    ) -> Order | None:

        stmt = (
            select(Order)
            .join(Shipment, Shipment.order_id == Order.id)
            .where(
                Order.user_id == user_id,
                Shipment.tracking_number.ilike(tracking_number.strip()),
            )
            .options(
                selectinload(Order.items).selectinload(OrderItem.product_variant),
                selectinload(Order.shipments).selectinload(Shipment.items),
                selectinload(Order.payments),
            )
            .limit(1)
        )

        result = await self.session.execute(stmt)
        return result.scalars().first()

    # =========================================================
    # SEARCH ORDERS BY PRODUCT NAME
    # =========================================================

    async def search_orders_by_product_name(
        self,
        user_id: int,
        query: str,
    ) -> list[Order]:

        stmt = (
            select(Order)
            .join(OrderItem, OrderItem.order_id == Order.id)
            .where(
                Order.user_id == user_id,
                OrderItem.product_name_snapshot.ilike(f"%{query.strip()}%"),
            )
            .options(
                selectinload(Order.items).selectinload(OrderItem.product_variant),
                selectinload(Order.shipments).selectinload(Shipment.items),
                selectinload(Order.payments),
            )
            .order_by(Order.created_at.desc())
        )

        result = await self.session.execute(stmt)
        return list(result.scalars().unique().all())

    # =========================================================
    # CANCEL ORDER
    # =========================================================

    async def cancel_order(
        self,
        user_id: int,
        order_number: str,
    ) -> tuple[bool, str, Order | None]:

        order = await self.get_order_by_number(user_id, order_number)

        if order is None:
            return False, f"Order '{order_number}' was not found.", None

        if order.status.lower() in ["delivered", "completed"]:
            return (
                False,
                f"Order '{order_number}' is already delivered and cannot be cancelled. You can initiate a return instead.",
                order,
            )

        if order.status.lower() in ["shipped"]:
            return (
                False,
                f"Order '{order_number}' has already been shipped and cannot be cancelled directly. Please contact support or request a return upon delivery.",
                order,
            )

        if order.status.lower() in ["cancelled"]:
            return (
                False,
                f"Order '{order_number}' is already cancelled.",
                order,
            )

        order.status = "cancelled"
        for shipment in order.shipments:
            if shipment.status.lower() not in ["delivered", "in_transit"]:
                shipment.status = "cancelled"

        await self.session.commit()
        await self.session.refresh(order)

        return True, f"Order '{order_number}' has been successfully cancelled.", order

    # =========================================================
    # ADDRESSES
    # =========================================================

    async def get_user_addresses(
        self,
        user_id: int,
    ) -> list[Address]:

        stmt = (
            select(Address)
            .where(Address.user_id == user_id)
            .order_by(Address.is_default.desc(), Address.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_default_address(
        self,
        user_id: int,
    ) -> Address | None:

        stmt = (
            select(Address)
            .where(Address.user_id == user_id, Address.is_default.is_(True))
            .limit(1)
        )
        result = await self.session.execute(stmt)
        address = result.scalars().first()

        if address is None:
            stmt_any = (
                select(Address)
                .where(Address.user_id == user_id)
                .order_by(Address.created_at.desc())
                .limit(1)
            )
            result_any = await self.session.execute(stmt_any)
            address = result_any.scalars().first()

        return address

    async def get_address_by_id(
        self,
        user_id: int,
        address_id: int,
    ) -> Address | None:

        stmt = (
            select(Address)
            .where(Address.user_id == user_id, Address.id == address_id)
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    # =========================================================
    # PLACE ORDER FROM CART
    # =========================================================

    async def create_order_from_cart(
        self,
        user_id: int,
        address_id: int | None = None,
        payment_method: str = "cod",
    ) -> tuple[bool, str, Order | None]:

        # 1. Fetch user's cart
        cart_stmt = (
            select(Cart)
            .where(Cart.user_id == user_id)
            .options(
                selectinload(Cart.items)
                .selectinload(CartItem.product_variant)
                .selectinload(ProductVariant.product)
            )
            .limit(1)
        )
        cart_res = await self.session.execute(cart_stmt)
        cart = cart_res.scalars().first()

        if cart is None or not cart.items:
            return False, "Your cart is empty. Please add items to your cart before placing an order.", None

        # 2. Check stock availability for all items
        for item in cart.items:
            variant = item.product_variant
            if not variant.is_active:
                return False, f"Product '{variant.name}' is no longer active and cannot be ordered.", None
            if variant.stock_quantity < item.quantity:
                return (
                    False,
                    f"Insufficient stock for '{variant.name}'. Requested: {item.quantity}, Available: {variant.stock_quantity}.",
                    None,
                )

        # 3. Resolve shipping address
        address: Address | None = None
        if address_id:
            address = await self.get_address_by_id(user_id, address_id)
        else:
            address = await self.get_default_address(user_id)

        if address is None:
            return False, "No delivery address found. Please add a shipping address before checkout.", None

        address_snapshot = {
            "recipient_name": address.recipient_name,
            "address_line1": address.address_line1,
            "address_line2": address.address_line2,
            "city": address.city,
            "state": address.state,
            "postal_code": address.postal_code,
            "country": address.country,
            "phone": address.phone,
        }

        # 4. Calculate amounts
        subtotal = Decimal("0.00")
        total_discount = Decimal("0.00")

        for item in cart.items:
            variant = item.product_variant
            item_price = variant.price * item.quantity
            item_discount = variant.discount * item.quantity
            subtotal += item_price
            total_discount += item_discount

        # Shipping: free if subtotal > 500, else 50
        shipping_amount = Decimal("0.00") if (subtotal - total_discount) >= Decimal("500.00") else Decimal("50.00")
        # Tax: 18% standard GST on discounted subtotal
        taxable_amount = max(Decimal("0.00"), subtotal - total_discount)
        tax_amount = (taxable_amount * Decimal("0.18")).quantize(Decimal("0.01"))
        total_amount = taxable_amount + shipping_amount + tax_amount

        # 5. Generate order number
        count_stmt = select(func.count(Order.id))
        total_orders_count = (await self.session.execute(count_stmt)).scalar() or 0
        order_number = f"ORD-2026-{(total_orders_count + 1):04d}"

        # 6. Create Order
        order = Order(
            user_id=user_id,
            order_number=order_number,
            status="processing",
            subtotal=subtotal,
            discount_amount=total_discount,
            shipping_amount=shipping_amount,
            tax_amount=tax_amount,
            total_amount=total_amount,
            shipping_address_snapshot=address_snapshot,
        )
        self.session.add(order)
        await self.session.flush()

        # 7. Create OrderItems and deduct inventory stock
        created_order_items = []
        for item in cart.items:
            variant = item.product_variant
            variant.stock_quantity -= item.quantity

            order_item = OrderItem(
                order_id=order.id,
                product_variant_id=variant.id,
                quantity=item.quantity,
                unit_price=(variant.price - variant.discount),
                product_name_snapshot=f"{variant.product.name} ({variant.name})",
            )
            self.session.add(order_item)
            created_order_items.append(order_item)

        await self.session.flush()

        # 8. Create Payment
        payment_status = "completed" if payment_method.lower() in ["upi", "card", "credit_card"] else "pending"
        payment = Payment(
            order_id=order.id,
            amount=total_amount,
            status=payment_status,
            payment_method=payment_method.lower(),
            transaction_reference=f"TXN-{random.randint(100000, 999999)}",
        )
        self.session.add(payment)

        # 9. Create Shipment
        now = datetime.now(timezone.utc)
        shipment = Shipment(
            order_id=order.id,
            tracking_number=f"TRK-{random.randint(100000, 999999)}",
            carrier="BlueDart",
            status="label_created",
            shipped_at=None,
            estimated_delivery_at=now + timedelta(days=3),
        )
        self.session.add(shipment)
        await self.session.flush()

        # 10. Link ShipmentItems
        for o_item in created_order_items:
            shipment_item = ShipmentItem(
                shipment_id=shipment.id,
                order_item_id=o_item.id,
                quantity=o_item.quantity,
            )
            self.session.add(shipment_item)

        # 11. Empty user's cart
        delete_cart_items_stmt = delete(CartItem).where(CartItem.cart_id == cart.id)
        await self.session.execute(delete_cart_items_stmt)

        await self.session.commit()

        # Reload order with relationships
        full_order = await self.get_order_by_number(user_id, order.order_number)
        return True, f"Order {order_number} has been successfully placed!", full_order

    # =========================================================
    # REORDER PAST ORDER ITEMS INTO CART
    # =========================================================

    async def reorder_to_cart(
        self,
        user_id: int,
        order_number: str,
    ) -> tuple[bool, str, list[dict]]:

        order = await self.get_order_by_number(user_id, order_number)
        if order is None:
            return False, f"Order '{order_number}' not found.", []

        # Get or create cart
        cart_stmt = select(Cart).where(Cart.user_id == user_id).limit(1)
        cart_res = await self.session.execute(cart_stmt)
        cart = cart_res.scalars().first()

        if cart is None:
            cart = Cart(user_id=user_id)
            self.session.add(cart)
            await self.session.flush()

        reordered_items = []
        for o_item in order.items:
            variant = await self.session.get(ProductVariant, o_item.product_variant_id)
            if not variant or not variant.is_active or variant.stock_quantity <= 0:
                continue

            qty_to_add = min(o_item.quantity, variant.stock_quantity)

            # Check existing cart item
            existing_stmt = select(CartItem).where(
                CartItem.cart_id == cart.id,
                CartItem.product_variant_id == variant.id,
            )
            existing = (await self.session.execute(existing_stmt)).scalars().first()

            if existing:
                existing.quantity += qty_to_add
            else:
                new_cart_item = CartItem(
                    cart_id=cart.id,
                    product_variant_id=variant.id,
                    quantity=qty_to_add,
                )
                self.session.add(new_cart_item)

            reordered_items.append({
                "product_name": o_item.product_name_snapshot,
                "quantity": qty_to_add,
            })

        await self.session.commit()
        return True, f"Re-added {len(reordered_items)} item(s) from order {order_number} to your cart.", reordered_items
