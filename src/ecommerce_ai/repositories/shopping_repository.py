from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from ecommerce_ai.models.product import Product, ProductVariant
from ecommerce_ai.models.shopping import (
    Cart,
    CartItem,
    Wishlist,
    WishlistItem,
)


class ShoppingRepository:

    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

    # =========================================================
    # CART
    # =========================================================

    async def get_cart(
        self,
        user_id: int,
    ):

        cart = await self._get_or_create_cart(
            user_id=user_id,
            create=False,
        )

        if cart is None:
            return []

        stmt = (
            select(
                CartItem,
                Product,
                ProductVariant,
            )
            .join(
                ProductVariant,
                ProductVariant.id
                == CartItem.product_variant_id,
            )
            .join(
                Product,
                Product.id
                == ProductVariant.product_id,
            )
            .where(
                CartItem.cart_id == cart.id,
            )
        )

        result = await self.session.execute(stmt)

        return result.all()

    async def add_to_cart(
        self,
        user_id: int,
        variant_id: int,
        quantity: int,
    ):

        variant = await self.session.get(
            ProductVariant,
            variant_id,
        )

        if quantity < 1:
            return {"success": False, "message": "Quantity must be at least 1."}

        # -----------------------------------------------------
        # Validate variant
        # -----------------------------------------------------

        if variant is None or not variant.is_active:
            return {
                "success": False,
                "message": "Active product variant not found.",
            }

        # -----------------------------------------------------
        # Validate stock
        # -----------------------------------------------------

        if variant.stock_quantity < quantity:
            return {
                "success": False,
                "message": (
                    f"Only {variant.stock_quantity} units "
                    "are in stock."
                ),
            }

        # -----------------------------------------------------
        # Get/Create user's cart
        # -----------------------------------------------------

        cart = await self._get_or_create_cart(
            user_id=user_id,
            create=True,
        )

        # -----------------------------------------------------
        # Find existing cart item
        # -----------------------------------------------------

        stmt = select(CartItem).where(
            CartItem.cart_id == cart.id,
            CartItem.product_variant_id == variant_id,
        )

        item = (
            await self.session.execute(stmt)
        ).scalar_one_or_none()

        # -----------------------------------------------------
        # Calculate new quantity
        # -----------------------------------------------------

        existing_quantity = (
            item.quantity
            if item is not None
            else 0
        )

        new_quantity = (
            existing_quantity + quantity
        )

        # -----------------------------------------------------
        # Validate total quantity
        # -----------------------------------------------------

        if new_quantity > variant.stock_quantity:
            return {
                "success": False,
                "message": (
                    f"Only {variant.stock_quantity} units "
                    "are in stock."
                ),
            }

        # -----------------------------------------------------
        # Update/Create item
        # -----------------------------------------------------

        if item:

            item.quantity = new_quantity

        else:

            self.session.add(
                CartItem(
                    cart_id=cart.id,
                    product_variant_id=variant_id,
                    quantity=quantity,
                )
            )

        # -----------------------------------------------------
        # Commit
        # -----------------------------------------------------

        await self.session.commit()

        return {
            "success": True,
            "message": "Item added to cart.",
            "quantity": new_quantity,
        }

    async def update_cart_item(
        self,
        user_id: int,
        variant_id: int,
        quantity: int,
    ):

        if quantity < 1:
            return {"success": False, "message": "Quantity must be at least 1."}

        cart = await self._get_or_create_cart(
            user_id=user_id,
            create=False,
        )

        if cart is None:
            return {
                "success": False,
                "message": "Cart item not found.",
            }

        stmt = (
            select(
                CartItem,
                ProductVariant,
            )
            .join(
                ProductVariant,
                ProductVariant.id
                == CartItem.product_variant_id,
            )
            .where(
                CartItem.cart_id == cart.id,
                CartItem.product_variant_id == variant_id,
            )
        )

        row = (
            await self.session.execute(stmt)
        ).first()

        if row is None:
            return {
                "success": False,
                "message": "Cart item not found.",
            }

        item, variant = row

        # -----------------------------------------------------
        # Validate variant and stock
        # -----------------------------------------------------

        if (
            not variant.is_active
            or quantity > variant.stock_quantity
        ):
            return {
                "success": False,
                "message": (
                    "Requested quantity is not available."
                ),
            }

        # -----------------------------------------------------
        # Update quantity
        # -----------------------------------------------------

        item.quantity = quantity

        await self.session.commit()

        return {
            "success": True,
            "message": "Cart quantity updated.",
            "quantity": quantity,
        }

    async def remove_from_cart(
        self,
        user_id: int,
        cart_item_id: int,
    ):

        cart = await self._get_or_create_cart(
            user_id=user_id,
            create=False,
        )

        if cart is None:
            return {
                "success": False,
                "message": "Cart item not found.",
            }

        item = await self.session.get(
            CartItem,
            cart_item_id,
        )

        # -----------------------------------------------------
        # Ownership check
        # -----------------------------------------------------

        if (
            item is None
            or item.cart_id != cart.id
        ):
            return {
                "success": False,
                "message": "Cart item not found.",
            }

        await self.session.delete(item)

        await self.session.commit()

        return {
            "success": True,
            "message": "Item removed from cart.",
        }

    async def clear_cart(self, user_id: int):
        cart = await self._get_or_create_cart(user_id=user_id, create=False)
        if cart is None:
            return {"success": True, "message": "Cart is already empty.", "removed_items": 0}

        result = await self.session.execute(
            delete(CartItem).where(CartItem.cart_id == cart.id)
        )
        await self.session.commit()
        return {
            "success": True,
            "message": "Cart cleared.",
            "removed_items": result.rowcount or 0,
        }

    # =========================================================
    # WISHLIST
    # =========================================================

    async def get_wishlist(
        self,
        user_id: int,
    ):

        wishlist = await self._get_or_create_wishlist(
            user_id=user_id,
            create=False,
        )

        if wishlist is None:
            return []

        stmt = (
            select(Product)
            .join(
                WishlistItem,
                WishlistItem.product_id
                == Product.id,
            )
            .where(
                WishlistItem.wishlist_id
                == wishlist.id,
            )
        )

        result = await self.session.execute(stmt)

        return list(result.scalars().all())

    async def add_to_wishlist(
        self,
        user_id: int,
        product_id: int,
    ):

        product = await self.session.get(
            Product,
            product_id,
        )

        if product is None:
            return {
                "success": False,
                "message": "Product not found.",
            }

        wishlist = await self._get_or_create_wishlist(
            user_id=user_id,
            create=True,
        )

        stmt = select(WishlistItem).where(
            WishlistItem.wishlist_id == wishlist.id,
            WishlistItem.product_id == product_id,
        )

        existing_item = (
            await self.session.execute(stmt)
        ).scalar_one_or_none()

        if existing_item:

            return {
                "success": True,
                "message": (
                    "Product is already in the wishlist."
                ),
            }

        self.session.add(
            WishlistItem(
                wishlist_id=wishlist.id,
                product_id=product_id,
            )
        )

        await self.session.commit()

        return {
            "success": True,
            "message": "Product added to wishlist.",
        }

    async def clear_wishlist(self, user_id: int):
        wishlist = await self._get_or_create_wishlist(
            user_id=user_id,
            create=False,
        )
        if wishlist is None:
            return {"success": True, "message": "Wishlist is already empty.", "removed_items": 0}

        result = await self.session.execute(
            delete(WishlistItem).where(WishlistItem.wishlist_id == wishlist.id)
        )
        await self.session.commit()
        return {
            "success": True,
            "message": "Wishlist cleared.",
            "removed_items": result.rowcount or 0,
        }

    async def remove_from_wishlist(
        self,
        user_id: int,
        product_id: int,
    ):

        wishlist = await self._get_or_create_wishlist(
            user_id=user_id,
            create=False,
        )

        if wishlist is None:
            return {
                "success": False,
                "message": "Wishlist item not found.",
            }

        stmt = select(WishlistItem).where(
            WishlistItem.wishlist_id == wishlist.id,
            WishlistItem.product_id == product_id,
        )

        item = (
            await self.session.execute(stmt)
        ).scalar_one_or_none()

        if item is None:
            return {
                "success": False,
                "message": "Wishlist item not found.",
            }

        await self.session.delete(item)

        await self.session.commit()

        return {
            "success": True,
            "message": "Product removed from wishlist.",
        }

    # =========================================================
    # PRIVATE HELPERS
    # =========================================================

    async def _get_or_create_cart(
        self,
        user_id: int,
        create: bool = True,
    ):

        stmt = (
            select(Cart)
            .where(
                Cart.user_id == user_id
            )
            .order_by(
                Cart.id.desc()
            )
            .limit(1)
        )

        cart = (
            await self.session.execute(stmt)
        ).scalar_one_or_none()

        if cart is None and create:

            cart = Cart(
                user_id=user_id
            )

            self.session.add(cart)

            await self.session.flush()

        return cart

    async def _get_or_create_wishlist(
        self,
        user_id: int,
        create: bool = True,
    ):

        stmt = (
            select(Wishlist)
            .where(
                Wishlist.user_id == user_id
            )
            .order_by(
                Wishlist.id.desc()
            )
            .limit(1)
        )

        wishlist = (
            await self.session.execute(stmt)
        ).scalar_one_or_none()

        if wishlist is None and create:

            wishlist = Wishlist(
                user_id=user_id
            )

            self.session.add(wishlist)

            await self.session.flush()

        return wishlist