from langchain_core.tools import tool

from ecommerce_ai.repositories.product_repository import (
    ProductRepository,
)
from ecommerce_ai.schemas.products import (
    ProductAvailabilityRequest,
    ProductDetailsRequest,
    ProductSearchRequest,
)
from ecommerce_ai.services.products import ProductService


def create_product_tools(
    repository: ProductRepository,
):

    service = ProductService(repository)

    # ========================================================
    # SEARCH PRODUCTS
    # ========================================================

    @tool
    async def search_products(
        request: ProductSearchRequest,
    ):
        """
        Search products from the e-commerce catalog.

        Use this tool when the user wants to:
        - find products
        - search products
        - browse products
        - filter products
        - find products by brand
        - filter by price
        - filter by category
        - filter by specifications
        - find available products

        The database is the source of truth.
        """

        return await service.search_products(
            request
        )

    # ========================================================
    # LIST COMPLETE CATALOG
    # ========================================================

    @tool
    async def list_all_products():
        """
        Return every product currently stored in the product database, with
        category and variant details. Use this for broad catalog requests such
        as "list me the products", "show all products", or "list every product
        in the store". Do not ask the user to pick a category before calling it.
        """
        return await service.list_all_products()

    # ========================================================
    # PRODUCT DETAILS
    # ========================================================

    @tool
    async def get_product_details(
        request: ProductDetailsRequest,
    ):
        """
        Get complete information about a specific product.

        Use this when the user asks about:
        - a specific product
        - product specifications
        - product variants
        - price
        - discount
        - rating
        - product description
        """

        result = await service.get_product_details(
            request
        )

        if result is None:
            return {
                "found": False,
                "message": "Product not found.",
            }

        return result

    # ========================================================
    # AVAILABILITY
    # ========================================================

    @tool
    async def check_product_availability(
        request: ProductAvailabilityRequest,
    ):
        """
        Check whether a product or product variant
        is currently available.

        Returns the current stock quantity and
        active status from the database.
        """

        result = await service.check_availability(
            request
        )

        if result is None:
            return {
                "found": False,
                "message": "Product or variant not found.",
            }

        return result

    # ========================================================
    # COMPARISON
    # ========================================================

    @tool
    async def compare_products(
        product_ids: list[int],
    ):
        """
        Compare 2 to 4 products using their product IDs.

        Use this after identifying the products that
        the user wants to compare.

        The comparison data comes directly from the
        product database.
        """

        if len(product_ids) < 2:
            return {
                "error": "At least 2 products are required for comparison."
            }

        if len(product_ids) > 4:
            return {
                "error": "A maximum of 4 products can be compared."
            }

        return await service.compare_products(
            product_ids
        )

    return [
        search_products,
        list_all_products,
        get_product_details,
        check_product_availability,
        compare_products,
    ]