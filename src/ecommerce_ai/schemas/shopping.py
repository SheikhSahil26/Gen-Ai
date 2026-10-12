from pydantic import BaseModel, Field


class CartItemRequest(BaseModel):
    user_id: int = Field(description="ID of the signed-in user")
    variant_id: int = Field(description="Product variant ID")
    quantity: int = Field(default=1, ge=1)


class CartRequest(BaseModel):
    user_id: int = Field(description="ID of the signed-in user")


class UpdateCartItemRequest(CartItemRequest):
    pass


class RemoveCartItemRequest(BaseModel):
    user_id: int = Field(description="ID of the signed-in user")
    cart_item_id: int


class WishlistItemRequest(BaseModel):
    user_id: int = Field(description="ID of the signed-in user")
    product_id: int


class RemoveWishlistItemRequest(WishlistItemRequest):
    pass
