from pydantic import BaseModel, Field


class OrderHistoryRequest(BaseModel):
    user_id: int = Field(
        description="ID of the signed-in user",
    )
    status: str | None = Field(
        default=None,
        description=(
            "Optional status filter: pending, processing, "
            "shipped, delivered, cancelled"
        ),
    )
    limit: int = Field(
        default=5,
        ge=1,
        le=50,
        description="Maximum number of orders to return",
    )


class OrderDetailsRequest(BaseModel):
    user_id: int = Field(
        description="ID of the signed-in user",
    )
    order_number: str = Field(
        description=(
            "Order number identifier, e.g. ORD-2026-0001"
        ),
    )


class TrackOrderRequest(BaseModel):
    user_id: int = Field(
        description="ID of the signed-in user",
    )
    order_number: str | None = Field(
        default=None,
        description="Order number to track",
    )
    tracking_number: str | None = Field(
        default=None,
        description="Shipment tracking number",
    )


class CompareOrderWithCartRequest(BaseModel):
    user_id: int = Field(
        description="ID of the signed-in user",
    )
    order_number: str | None = Field(
        default=None,
        description=(
            "Specific order number to compare with cart; "
            "if omitted, latest order is used"
        ),
    )


class SearchPastOrdersRequest(BaseModel):
    user_id: int = Field(
        description="ID of the signed-in user",
    )
    product_name: str = Field(
        description=(
            "Product name or keyword to search in "
            "past orders"
        ),
    )


class CancelOrderRequest(BaseModel):
    user_id: int = Field(
        description="ID of the signed-in user",
    )
    order_number: str = Field(
        description="Order number to cancel",
    )
