from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ecommerce_ai.models.product import (
    Category,
    Product,
    ProductVariant,
)
from ecommerce_ai.schemas.products import (
    ProductAvailabilityRequest,
    ProductDetailsRequest,
    ProductSearchRequest,
)


class ProductRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    # ========================================================
    # SEARCH PRODUCTS
    # ========================================================

    async def search_products(
        self,
        request: ProductSearchRequest,
    ) -> list[tuple[Product, ProductVariant]]:

        stmt = (
            select(Product, ProductVariant)
            .join(
                ProductVariant,
                ProductVariant.product_id == Product.id,
            )
            .join(
                Category,
                Category.id == Product.category_id,
            )
        )

        # ----------------------------------------------------
        # Text search
        # ----------------------------------------------------

        if request.query:
            search_pattern = f"%{request.query}%"

            stmt = stmt.where(
                Product.name.ilike(search_pattern)
                | Product.description.ilike(search_pattern)
                | Product.brand.ilike(search_pattern)
            )

        # ----------------------------------------------------
        # Category
        # ----------------------------------------------------

        if request.category:
            category_pattern = f"%{request.category}%"

            stmt = stmt.where(
                Category.name.ilike(category_pattern)
                | Category.slug.ilike(category_pattern)
            )

        # ----------------------------------------------------
        # Brand
        # ----------------------------------------------------

        if request.brand:
            stmt = stmt.where(
                Product.brand.ilike(
                    f"%{request.brand}%"
                )
            )

        # ----------------------------------------------------
        # Minimum price
        # ----------------------------------------------------

        if request.min_price is not None:
            stmt = stmt.where(
                ProductVariant.price >= request.min_price
            )

        # ----------------------------------------------------
        # Maximum price
        # ----------------------------------------------------

        if request.max_price is not None:
            stmt = stmt.where(
                ProductVariant.price <= request.max_price
            )

        # ----------------------------------------------------
        # Specifications
        # ----------------------------------------------------

        for key, value in request.specifications.items():

            stmt = stmt.where(
                Product.specifications[key].as_string()
                == str(value)
            )

        # ----------------------------------------------------
        # Availability
        # ----------------------------------------------------

        if request.available_only:
            stmt = stmt.where(
                ProductVariant.stock_quantity > 0,
                ProductVariant.is_active.is_(True),
            )

        # ----------------------------------------------------
        # Limit
        # ----------------------------------------------------

        stmt = stmt.limit(request.limit)

        result = await self.session.execute(stmt)

        print(result.all())

        return result.all()

    # ========================================================
    # LIST ALL PRODUCTS
    # ========================================================

    async def list_all_products(
        self,
    ) -> list[tuple[Product, Category, list[ProductVariant]]]:
        stmt = (
            select(Product, Category, ProductVariant)
            .join(Category, Category.id == Product.category_id)
            .outerjoin(
                ProductVariant,
                ProductVariant.product_id == Product.id,
            )
            .order_by(Product.id, ProductVariant.id)
        )
        rows = (await self.session.execute(stmt)).all()

        products: dict[int, tuple[Product, Category, list[ProductVariant]]] = {}
        for product, category, variant in rows:
            if product.id not in products:
                products[product.id] = (product, category, [])
            if variant is not None:
                products[product.id][2].append(variant)

        return list(products.values())

    # ========================================================
    # GET PRODUCT DETAILS
    # ========================================================

    async def get_product_details(
        self,
        request: ProductDetailsRequest,
    ) -> tuple[Product, Category, list[ProductVariant]] | None:

        product_stmt = (
            select(Product, Category)
            .join(
                Category,
                Category.id == Product.category_id,
            )
            .where(
                Product.id == request.product_id
            )
        )

        result = await self.session.execute(
            product_stmt
        )

        product_row = result.first()

        if product_row is None:
            return None

        product, category = product_row

        variant_stmt = select(ProductVariant).where(
            ProductVariant.product_id == product.id
        )

        if request.variant_id is not None:
            variant_stmt = variant_stmt.where(
                ProductVariant.id == request.variant_id
            )

        variant_result = await self.session.execute(
            variant_stmt
        )

        variants = list(variant_result.scalars().all())

        return product, category, variants

    # ========================================================
    # GET PRODUCT AVAILABILITY
    # ========================================================

    async def get_product_availability(
        self,
        request: ProductAvailabilityRequest,
    ) -> tuple[Product, ProductVariant] | None:

        stmt = (
            select(Product, ProductVariant)
            .join(
                ProductVariant,
                ProductVariant.product_id == Product.id,
            )
            .where(
                Product.id == request.product_id
            )
        )

        if request.variant_id is not None:
            stmt = stmt.where(
                ProductVariant.id == request.variant_id
            )

        stmt = stmt.limit(1)

        result = await self.session.execute(stmt)

        return result.first()

    # ========================================================
    # GET PRODUCTS FOR COMPARISON
    # ========================================================

    async def get_products_for_comparison(
        self,
        product_ids: list[int],
    ) -> list[
        tuple[
            Product,
            Category,
            list[ProductVariant],
        ]
    ]:

        product_stmt = (
            select(Product, Category)
            .join(
                Category,
                Category.id == Product.category_id,
            )
            .where(
                Product.id.in_(product_ids)
            )
        )

        result = await self.session.execute(
            product_stmt
        )

        product_rows = result.all()

        if not product_rows:
            return []

        products = [row[0] for row in product_rows]
        categories = {
            row[0].id: row[1]
            for row in product_rows
        }

        variant_stmt = select(ProductVariant).where(
            ProductVariant.product_id.in_(
                product_ids
            )
        )

        variant_result = await self.session.execute(
            variant_stmt
        )

        variants = variant_result.scalars().all()

        variants_by_product: dict[
            int,
            list[ProductVariant]
        ] = {}

        for variant in variants:
            variants_by_product.setdefault(
                variant.product_id,
                []
            ).append(variant)

        return [
            (
                product,
                categories[product.id],
                variants_by_product.get(
                    product.id,
                    [],
                ),
            )
            for product in products
        ]