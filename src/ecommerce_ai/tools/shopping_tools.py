from typing import Annotated

from langchain_core.tools import tool
from pydantic import Field

from ecommerce_ai.auth.user_context import get_user_id
from ecommerce_ai.repositories.product_repository import ProductRepository
from ecommerce_ai.repositories.shopping_repository import ShoppingRepository
from ecommerce_ai.services.shopping import ShoppingService


def create_shopping_tools(
    repository: ShoppingRepository,
    product_repository: ProductRepository,
):

    service = ShoppingService(
        repository=repository,
        product_repository=product_repository,
    )

    # =========================================================
    # Product Discovery
    # =========================================================

    @tool
    async def find_products_for_shopping(
        query: str,
    ):
        """
        Find matching products and active variants, including current stock.

        Use this before cart or wishlist changes when the user refers to a
        product using natural language. Cart actions require available stock;
        wishlist actions do not.
        """

        return await service.find_products(
            query=query
        )

    # =========================================================
    # Cart
    # =========================================================

    @tool
    async def view_cart():
        """
        Show all items and prices in the current user's
        shopping cart.
        """

        user_id = get_user_id()

        return await service.get_cart(
            user_id=user_id
        )

    @tool
    async def add_to_cart(
        variant_id: int,
        quantity: Annotated[int, Field(ge=1)] = 1,
    ):
        """
        Add a product variant to the current user's cart.

        The user ID is obtained internally from the
        authenticated user context.
        """

        user_id = get_user_id()

        return await service.add_to_cart(
            user_id=user_id,
            variant_id=variant_id,
            quantity=quantity,
        )

    @tool
    async def update_cart_quantity(
        variant_id: int,
        quantity: Annotated[int, Field(ge=1)],
    ):
        """
        Update the quantity of a product variant in the
        current user's cart.
        """

        user_id = get_user_id()

        return await service.update_cart_quantity(
            user_id=user_id,
            variant_id=variant_id,
            quantity=quantity,
        )

    @tool
    async def clear_cart():
        """Remove every item from the current user's cart."""
        return await service.clear_cart(user_id=get_user_id())

    @tool
    async def remove_from_cart(
        cart_item_id: int,
    ):
        """
        Remove a cart item from the current user's cart.
        """

        user_id = get_user_id()

        return await service.remove_from_cart(
            user_id=user_id,
            cart_item_id=cart_item_id,
        )

    # =========================================================
    # Wishlist
    # =========================================================

    @tool
    async def view_wishlist():
        """
        Show the current user's wishlist.
        """

        user_id = get_user_id()

        return await service.get_wishlist(
            user_id=user_id
        )

    @tool
    async def add_to_wishlist(
        product_id: int,
    ):
        """
        Add a product to the current user's wishlist.
        """

        user_id = get_user_id()

        return await service.add_to_wishlist(
            user_id=user_id,
            product_id=product_id,
        )

    @tool
    async def clear_wishlist():
        """Remove every item from the current user's wishlist."""
        return await service.clear_wishlist(user_id=get_user_id())

    @tool
    async def remove_from_wishlist(
        product_id: int,
    ):
        """
        Remove a product from the current user's wishlist.
        """

        user_id = get_user_id()

        return await service.remove_from_wishlist(
            user_id=user_id,
            product_id=product_id,
        )

    return [
        find_products_for_shopping,
        view_cart,
        add_to_cart,
        update_cart_quantity,
        clear_cart,
        remove_from_cart,
        view_wishlist,
        add_to_wishlist,
        remove_from_wishlist,
        clear_wishlist,
    ]