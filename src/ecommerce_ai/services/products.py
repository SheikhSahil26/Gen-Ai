from ecommerce_ai.repositories.product_repository import (
    ProductRepository,
)
from ecommerce_ai.schemas.products import (
    ProductAvailabilityRequest,
    ProductAvailabilityResult,
    ProductComparisonResult,
    ProductDetailsRequest,
    ProductResult,
    ProductSearchRequest,
    ProductSearchResult,
    ProductVariantResult,
)


class ProductService:

    def __init__(
        self,
        repository: ProductRepository,
    ):
        self.repository = repository

    # ========================================================
    # SEARCH
    # ========================================================

    async def search_products(
        self,
        request: ProductSearchRequest,
    ) -> list[ProductSearchResult]:

        print(request,"this is request!!!!!")

        rows = await self.repository.search_products(
            request
        )

        print(rows,"this are the rows in product service!!")

        results: list[ProductSearchResult] = []

        for product, variant in rows:

            specifications = (
                product.specifications
                or {}
            )

            results.append(
                ProductSearchResult(
                    product_id=product.id,
                    name=product.name,
                    brand=product.brand,
                    description=product.description,
                    rating=product.rating,
                    variant_id=variant.id,
                    sku=variant.sku,
                    variant_name=variant.name,
                    price=variant.price,
                    discount=variant.discount,
                    stock_quantity=variant.stock_quantity,
                    is_active=variant.is_active,
                    specifications=specifications,
                )
            )

        return results

    # ========================================================
    # LIST ALL PRODUCTS
    # ========================================================

    async def list_all_products(self) -> list[ProductResult]:
        rows = await self.repository.list_all_products()
        return [
            ProductResult(
                id=product.id,
                name=product.name,
                brand=product.brand,
                description=product.description,
                rating=product.rating,
                specifications=product.specifications or {},
                category_id=category.id,
                category_name=category.name,
                variants=[
                    ProductVariantResult(
                        id=variant.id,
                        sku=variant.sku,
                        name=variant.name,
                        price=variant.price,
                        discount=variant.discount,
                        stock_quantity=variant.stock_quantity,
                        is_active=variant.is_active,
                        specifications=variant.specifications or {},
                    )
                    for variant in variants
                ],
            )
            for product, category, variants in rows
        ]

    # ========================================================
    # PRODUCT DETAILS
    # ========================================================

    async def get_product_details(
        self,
        request: ProductDetailsRequest,
    ) -> ProductResult | None:

        result = (
            await self.repository.get_product_details(
                request
            )
        )

        if result is None:
            return None

        product, category, variants = result

        variant_results = [
            ProductVariantResult(
                id=variant.id,
                sku=variant.sku,
                name=variant.name,
                price=variant.price,
                discount=variant.discount,
                stock_quantity=variant.stock_quantity,
                is_active=variant.is_active,
                specifications=(
                    variant.specifications
                    or {}
                ),
            )
            for variant in variants
        ]

        return ProductResult(
            id=product.id,
            name=product.name,
            brand=product.brand,
            description=product.description,
            rating=product.rating,
            specifications=(
                product.specifications
                or {}
            ),
            category_id=category.id,
            category_name=category.name,
            variants=variant_results,
        )

    # ========================================================
    # AVAILABILITY
    # ========================================================

    async def check_availability(
        self,
        request: ProductAvailabilityRequest,
    ) -> ProductAvailabilityResult | None:

        result = (
            await self.repository
            .get_product_availability(request)
        )

        if result is None:
            return None

        product, variant = result

        return ProductAvailabilityResult(
            product_id=product.id,
            product_name=product.name,
            variant_id=variant.id,
            variant_name=variant.name,
            available=(
                variant.is_active
                and variant.stock_quantity > 0
            ),
            stock_quantity=variant.stock_quantity,
            is_active=variant.is_active,
        )
    # ========================================================
    # COMPARISON
    # ========================================================

    async def compare_products(
        self,
        product_ids: list[int],
    ) -> ProductComparisonResult:

        rows = (
            await self.repository
            .get_products_for_comparison(
                product_ids
            )
        )

        products: list[ProductResult] = []

        for product, category, variants in rows:

            variant_results = [
                ProductVariantResult(
                    id=variant.id,
                    sku=variant.sku,
                    name=variant.name,
                    price=variant.price,
                    discount=variant.discount,
                    stock_quantity=variant.stock_quantity,
                    is_active=variant.is_active,
                    specifications=(
                        variant.specifications
                        or {}
                    ),
                )
                for variant in variants
            ]

            products.append(
                ProductResult(
                    id=product.id,
                    name=product.name,
                    brand=product.brand,
                    description=product.description,
                    rating=product.rating,
                    specifications=(
                        product.specifications
                        or {}
                    ),
                    category_id=category.id,
                    category_name=category.name,
                    variants=variant_results,
                )
            )

        return ProductComparisonResult(
            products=products
        )