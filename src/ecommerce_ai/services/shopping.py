from ecommerce_ai.repositories.product_repository import ProductRepository
from ecommerce_ai.repositories.shopping_repository import ShoppingRepository
from ecommerce_ai.schemas.products import ProductSearchRequest


class ShoppingService:

    def __init__(
        self,
        repository: ShoppingRepository,
        product_repository: ProductRepository,
    ):
        self.repository = repository
        self.product_repository = product_repository

    # =========================================================
    # Product Discovery for Shopping
    # =========================================================

    async def find_products(self, query: str):

        rows = await self.product_repository.search_products(
            ProductSearchRequest(
                query=query,
                available_only=False,
            )
        )

        return [
            {
                "product_id": product.id,
                "name": product.name,
                "variant_id": variant.id,
                "variant_name": variant.name,
                "sku": variant.sku,
                "price": str(variant.price),
                "stock_quantity": variant.stock_quantity,
            }
            for product, variant in rows
            if variant.is_active
        ]

    # =========================================================
    # Cart
    # =========================================================

    async def get_cart(self, user_id: int):

        rows = await self.repository.get_cart(
            user_id
        )

        return [
            {
                "cart_item_id": item.id,
                "product_id": product.id,
                "product_name": product.name,
                "variant_id": variant.id,
                "variant_name": variant.name,
                "quantity": item.quantity,
                "unit_price": str(variant.price),
                "unit_discount": str(variant.discount),
                "effective_unit_price": str(
                    variant.price - variant.discount
                ),
                "line_total": str(
                    variant.price * item.quantity
                ),
                "discount_total": str(
                    variant.discount * item.quantity
                ),
                "total_after_discount": str(
                    (variant.price - variant.discount) * item.quantity
                ),
            }
            for item, product, variant in rows
        ]

    async def add_to_cart(
        self,
        user_id: int,
        variant_id: int,
        quantity: int,
    ):

        return await self.repository.add_to_cart(
            user_id=user_id,
            variant_id=variant_id,
            quantity=quantity,
        )

    async def update_cart_quantity(
        self,
        user_id: int,
        variant_id: int,
        quantity: int,
    ):

        return await self.repository.update_cart_item(
            user_id=user_id,
            variant_id=variant_id,
            quantity=quantity,
        )

    async def remove_from_cart(
        self,
        user_id: int,
        cart_item_id: int,
    ):

        return await self.repository.remove_from_cart(
            user_id=user_id,
            cart_item_id=cart_item_id,
        )

    async def clear_cart(self, user_id: int):
        return await self.repository.clear_cart(user_id=user_id)

    # =========================================================
    # Wishlist
    # =========================================================

    async def get_wishlist(self, user_id: int):

        products = await self.repository.get_wishlist(
            user_id
        )

        return [
            {
                "product_id": product.id,
                "name": product.name,
                "brand": product.brand,
            }
            for product in products
        ]

    async def add_to_wishlist(
        self,
        user_id: int,
        product_id: int,
    ):

        return await self.repository.add_to_wishlist(
            user_id=user_id,
            product_id=product_id,
        )

    async def clear_wishlist(self, user_id: int):
        return await self.repository.clear_wishlist(user_id=user_id)

    async def remove_from_wishlist(
        self,
        user_id: int,
        product_id: int,
    ):

        return await self.repository.remove_from_wishlist(
            user_id=user_id,
            product_id=product_id,
        )