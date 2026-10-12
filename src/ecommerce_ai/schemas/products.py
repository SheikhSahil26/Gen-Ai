from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field


# ============================================================
# PRODUCT SEARCH
# ============================================================

class ProductSearchRequest(BaseModel):
    query: str | None = None
    category: str | None = None
    brand: str | None = None

    min_price: Decimal | None = None
    max_price: Decimal | None = None

    specifications: dict[str, Any] = Field(
        default_factory=dict
    )

    available_only: bool = True

    limit: int = Field(
        default=10,
        ge=1,
        le=50,
    )


class ProductSearchResult(BaseModel):
    product_id: int
    name: str
    brand: str | None
    description: str | None
    rating: float | None

    variant_id: int
    sku: str
    variant_name: str

    price: Decimal
    discount: Decimal
    stock_quantity: int
    is_active: bool

    specifications: dict[str, Any]


# ============================================================
# PRODUCT DETAILS
# ============================================================

class ProductDetailsRequest(BaseModel):
    product_id: int

    variant_id: int | None = None


class ProductVariantResult(BaseModel):
    id: int
    sku: str
    name: str
    price: Decimal
    discount: Decimal
    stock_quantity: int
    is_active: bool
    specifications: dict[str, Any]


class ProductResult(BaseModel):
    id: int
    name: str
    brand: str | None
    description: str | None
    rating: float | None
    specifications: dict[str, Any]

    category_id: int
    category_name: str

    variants: list[ProductVariantResult]


# ============================================================
# AVAILABILITY
# ============================================================

class ProductAvailabilityRequest(BaseModel):
    product_id: int

    variant_id: int | None = None


class ProductAvailabilityResult(BaseModel):
    product_id: int
    product_name: str

    variant_id: int
    variant_name: str

    available: bool
    stock_quantity: int
    is_active: bool


# ============================================================
# PRODUCT COMPARISON
# ============================================================

class ProductComparisonRequest(BaseModel):
    product_ids: list[int] = Field(
        min_length=2,
        max_length=4,
    )


class ProductComparisonResult(BaseModel):
    products: list[ProductResult]