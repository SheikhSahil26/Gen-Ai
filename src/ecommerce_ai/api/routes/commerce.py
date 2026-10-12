from decimal import Decimal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ecommerce_ai.api.dependencies import get_db_session
from ecommerce_ai.auth.user_context import get_user_id
from ecommerce_ai.repositories.order_repository import OrderRepository
from ecommerce_ai.repositories.product_repository import ProductRepository
from ecommerce_ai.repositories.shopping_repository import ShoppingRepository
from ecommerce_ai.services.order import OrderService
from ecommerce_ai.services.shopping import ShoppingService

router = APIRouter(tags=["Commerce"])


@router.get("/cart")
async def get_cart(
    session: AsyncSession = Depends(get_db_session),
):
    service = ShoppingService(
        repository=ShoppingRepository(session),
        product_repository=ProductRepository(session),
    )
    items = await service.get_cart(user_id=get_user_id())
    subtotal = sum((Decimal(item["line_total"]) for item in items), Decimal("0.00"))
    discount = sum((Decimal(item["discount_total"]) for item in items), Decimal("0.00"))
    total = sum((Decimal(item["total_after_discount"]) for item in items), Decimal("0.00"))

    return {
        "items": items,
        "item_count": sum(item["quantity"] for item in items),
        "subtotal": str(subtotal),
        "discount": str(discount),
        "total": str(total),
        "currency": "INR",
    }


@router.get("/orders")
async def get_orders(
    limit: int = Query(default=20, ge=1, le=50),
    session: AsyncSession = Depends(get_db_session),
):
    service = OrderService(repository=OrderRepository(session))
    history = await service.get_order_history(
        user_id=get_user_id(),
        limit=limit,
    )
    return {
        "orders": history["orders"],
        "total_orders": history["total_orders"],
        "currency": "INR",
    }
