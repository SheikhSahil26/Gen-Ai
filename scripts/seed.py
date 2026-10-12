
"""
Development database seed script for the Multi-AI E-Commerce project.

WARNING:
    This script DELETES ALL EXISTING DATA.

    Use this ONLY for local development/testing.
    NEVER run this against a production database.

Run:
    uv run python scripts/seed.py
"""

import asyncio
from datetime import datetime, timezone
from decimal import Decimal

from pwdlib import PasswordHash
from sqlalchemy import text

from ecommerce_ai.db.database import AsyncSessionLocal
from ecommerce_ai.models.base import Base

# ==============================================================
# IMPORT ALL MODELS
# ==============================================================
#
# Importing all model modules ensures SQLAlchemy has all tables
# and relationships registered in Base.metadata before we use them.
#

from ecommerce_ai.models.user import User
from ecommerce_ai.models.product import (
    Category,
    Product,
    ProductVariant,
)
from ecommerce_ai.models.shopping import (
    Address,
    Cart,
    CartItem,
    Wishlist,
    WishlistItem,
)
from ecommerce_ai.models.order import (
    Order,
    OrderItem,
    Payment,
    Shipment,
    ShipmentItem,
)
from ecommerce_ai.models.support import (
    Return,
    ReturnItem,
    Refund,
    Review,
    ProductDocument,
    DocumentChunk,
    AuditLog,
)


# ==============================================================
# PASSWORD CONFIGURATION
# ==============================================================

password_hasher = PasswordHash.recommended()

SEED_PASSWORD = "password123"


# ==============================================================
# DATABASE RESET
# ==============================================================

async def reset_database(session):
    """
    Remove all existing rows and reset PostgreSQL sequences.

    RESTART IDENTITY means:
        First inserted User -> id 1
        Second inserted User -> id 2

    CASCADE handles foreign-key dependencies.
    """

    print("Resetting database...")

    table_names = [
        table.name
        for table in Base.metadata.sorted_tables
    ]

    if not table_names:
        raise RuntimeError(
            "No tables found in Base.metadata. "
            "Make sure all models are imported."
        )

    quoted_tables = ", ".join(
        f'"{table_name}"'
        for table_name in table_names
    )

    await session.execute(
        text(
            f"TRUNCATE TABLE {quoted_tables} "
            "RESTART IDENTITY CASCADE"
        )
    )

    await session.commit()

    print("Database reset completed.")


# ==============================================================
# USERS
# ==============================================================

async def seed_users(session):
    password_hash = password_hasher.hash(SEED_PASSWORD)

    user1 = User(
        username="sahil",
        email="sahil@example.com",
        hashed_password=password_hash,
    )

    user2 = User(
        username="rahul",
        email="rahul@example.com",
        hashed_password=password_hash,
    )

    session.add_all([user1, user2])

    await session.flush()

    print(
        f"Created users: "
        f"{user1.id}={user1.username}, "
        f"{user2.id}={user2.username}"
    )

    return user1, user2


# ==============================================================
# CATEGORIES
# ==============================================================

async def seed_categories(session):
    laptops = Category(
        name="Laptops",
        slug="laptops",
        description=(
            "Laptops for gaming, programming, "
            "business and general use."
        ),
    )

    smartphones = Category(
        name="Smartphones",
        slug="smartphones",
        description="Smartphones from different brands.",
    )

    headphones = Category(
        name="Headphones",
        slug="headphones",
        description=(
            "Wireless and wired headphones "
            "with different features."
        ),
    )

    accessories = Category(
        name="Accessories",
        slug="accessories",
        description=(
            "Computer, mobile and productivity accessories."
        ),
    )

    session.add_all(
        [
            laptops,
            smartphones,
            headphones,
            accessories,
        ]
    )

    await session.flush()

    return (
        laptops,
        smartphones,
        headphones,
        accessories,
    )


# ==============================================================
# PRODUCTS
# ==============================================================

async def seed_products(session, categories):
    (
        laptops,
        smartphones,
        headphones,
        accessories,
    ) = categories

    # ----------------------------------------------------------
    # LAPTOPS
    # ----------------------------------------------------------

    legion = Product(
        category_id=laptops.id,
        name="Lenovo Legion 5",
        description=(
            "Gaming laptop suitable for gaming, "
            "programming and demanding workloads."
        ),
        brand="Lenovo",
        rating=4.6,
        specifications={
            "processor": "AMD Ryzen 7 7840HS",
            "ram": "16GB",
            "storage": "512GB SSD",
            "display": "15.6 inch FHD 144Hz",
            "gpu": "NVIDIA RTX 4060",
        },
    )

    tuf = Product(
        category_id=laptops.id,
        name="ASUS TUF Gaming F15",
        description=(
            "Durable gaming laptop designed for "
            "gaming and performance workloads."
        ),
        brand="ASUS",
        rating=4.4,
        specifications={
            "processor": "Intel Core i7-12700H",
            "ram": "16GB",
            "storage": "512GB SSD",
            "display": "15.6 inch FHD 144Hz",
            "gpu": "NVIDIA RTX 4060",
        },
    )

    macbook = Product(
        category_id=laptops.id,
        name="MacBook Air M3",
        description=(
            "Thin and lightweight laptop powered "
            "by Apple's M3 chip."
        ),
        brand="Apple",
        rating=4.8,
        specifications={
            "processor": "Apple M3",
            "ram": "16GB",
            "storage": "512GB SSD",
            "display": "13.6 inch Retina",
            "gpu": "Integrated",
        },
    )

    # ----------------------------------------------------------
    # SMARTPHONES
    # ----------------------------------------------------------

    samsung = Product(
        category_id=smartphones.id,
        name="Samsung Galaxy S24",
        description=(
            "Premium Android smartphone with "
            "high-end performance."
        ),
        brand="Samsung",
        rating=4.7,
        specifications={
            "display": "6.2 inch AMOLED",
            "ram": "8GB",
            "storage": "256GB",
            "camera": "50MP",
            "battery": "4000mAh",
        },
    )

    iphone = Product(
        category_id=smartphones.id,
        name="iPhone 15",
        description=(
            "Apple smartphone powered by "
            "the A16 Bionic processor."
        ),
        brand="Apple",
        rating=4.7,
        specifications={
            "display": "6.1 inch OLED",
            "ram": "6GB",
            "storage": "128GB",
            "camera": "48MP",
            "battery": "3349mAh",
        },
    )

    # ----------------------------------------------------------
    # HEADPHONES
    # ----------------------------------------------------------

    sony = Product(
        category_id=headphones.id,
        name="Sony WH-1000XM5",
        description=(
            "Premium wireless over-ear headphones "
            "with active noise cancellation."
        ),
        brand="Sony",
        rating=4.8,
        specifications={
            "type": "Over-ear",
            "connectivity": "Bluetooth",
            "noise_cancellation": True,
            "battery": "30 hours",
        },
    )

    # ----------------------------------------------------------
    # ACCESSORIES
    # ----------------------------------------------------------

    logitech = Product(
        category_id=accessories.id,
        name="Logitech MX Master 3S",
        description=(
            "Wireless productivity mouse designed "
            "for professional workflows."
        ),
        brand="Logitech",
        rating=4.7,
        specifications={
            "connectivity": "Bluetooth",
            "buttons": 7,
            "dpi": 8000,
            "battery": "70 days",
        },
    )

    products = [
        legion,
        tuf,
        macbook,
        samsung,
        iphone,
        sony,
        logitech,
    ]

    session.add_all(products)

    await session.flush()

    return products


# ==============================================================
# PRODUCT VARIANTS
# ==============================================================

async def seed_product_variants(session, products):
    (
        legion,
        tuf,
        macbook,
        samsung,
        iphone,
        sony,
        logitech,
    ) = products

    legion_variant = ProductVariant(
        product_id=legion.id,
        sku="LEN-LEGION5-R7-4060",
        name="Legion 5 Ryzen 7 RTX 4060",
        price=Decimal("74999.00"),
        discount=Decimal("5000.00"),
        stock_quantity=15,
        specifications={
            "ram": "16GB",
            "storage": "512GB SSD",
            "gpu": "RTX 4060",
        },
        is_active=True,
    )

    tuf_variant = ProductVariant(
        product_id=tuf.id,
        sku="ASUS-TUF-F15-I7-4060",
        name="TUF F15 i7 RTX 4060",
        price=Decimal("69999.00"),
        discount=Decimal("4000.00"),
        stock_quantity=12,
        specifications={
            "ram": "16GB",
            "storage": "512GB SSD",
            "gpu": "RTX 4060",
        },
        is_active=True,
    )

    macbook_variant = ProductVariant(
        product_id=macbook.id,
        sku="APPLE-MBA-M3-16-512",
        name="MacBook Air M3 16GB 512GB",
        price=Decimal("119999.00"),
        discount=Decimal("5000.00"),
        stock_quantity=8,
        specifications={
            "ram": "16GB",
            "storage": "512GB",
        },
        is_active=True,
    )

    samsung_variant = ProductVariant(
        product_id=samsung.id,
        sku="SAMSUNG-S24-256-BLK",
        name="Galaxy S24 256GB Black",
        price=Decimal("64999.00"),
        discount=Decimal("7000.00"),
        stock_quantity=20,
        specifications={
            "storage": "256GB",
            "color": "Black",
        },
        is_active=True,
    )

    iphone_variant = ProductVariant(
        product_id=iphone.id,
        sku="APPLE-IP15-128-BLU",
        name="iPhone 15 128GB Blue",
        price=Decimal("59999.00"),
        discount=Decimal("6000.00"),
        stock_quantity=18,
        specifications={
            "storage": "128GB",
            "color": "Blue",
        },
        is_active=True,
    )

    sony_variant = ProductVariant(
        product_id=sony.id,
        sku="SONY-XM5-BLK",
        name="WH-1000XM5 Black",
        price=Decimal("29999.00"),
        discount=Decimal("3000.00"),
        stock_quantity=10,
        specifications={
            "color": "Black",
        },
        is_active=True,
    )

    logitech_variant = ProductVariant(
        product_id=logitech.id,
        sku="LOGI-MX3S-BLK",
        name="MX Master 3S Black",
        price=Decimal("8999.00"),
        discount=Decimal("1000.00"),
        stock_quantity=25,
        specifications={
            "color": "Black",
        },
        is_active=True,
    )

    variants = [
        legion_variant,
        tuf_variant,
        macbook_variant,
        samsung_variant,
        iphone_variant,
        sony_variant,
        logitech_variant,
    ]

    session.add_all(variants)

    await session.flush()

    return variants


# ==============================================================
# ADDRESSES
# ==============================================================

async def seed_addresses(session, users):
    user1, user2 = users

    address1 = Address(
        user_id=user1.id,
        label="Home",
        recipient_name="Sahil Sheikh",
        address_line1="VGEC Road",
        address_line2=None,
        city="Ahmedabad",
        state="Gujarat",
        postal_code="382028",
        country="India",
        phone="9999999999",
        is_default=True,
    )

    address2 = Address(
        user_id=user2.id,
        label="Home",
        recipient_name="Rahul Sharma",
        address_line1="Satellite Road",
        address_line2=None,
        city="Ahmedabad",
        state="Gujarat",
        postal_code="380015",
        country="India",
        phone="9888888888",
        is_default=True,
    )

    addresses = [
        address1,
        address2,
    ]

    session.add_all(addresses)

    await session.flush()

    return addresses


# ==============================================================
# CARTS
# ==============================================================

async def seed_carts(session, users, variants):
    user1, user2 = users

    (
        legion_variant,
        tuf_variant,
        macbook_variant,
        samsung_variant,
        iphone_variant,
        sony_variant,
        logitech_variant,
    ) = variants

    # ----------------------------------------------------------
    # CARTS
    # ----------------------------------------------------------

    cart1 = Cart(
        user_id=user1.id,
    )

    cart2 = Cart(
        user_id=user2.id,
    )

    carts = [
        cart1,
        cart2,
    ]

    session.add_all(carts)

    await session.flush()

    # ----------------------------------------------------------
    # CART ITEMS
    # ----------------------------------------------------------

    cart_item1 = CartItem(
        cart_id=cart1.id,
        product_variant_id=legion_variant.id,
        quantity=1,
    )

    cart_item2 = CartItem(
        cart_id=cart1.id,
        product_variant_id=sony_variant.id,
        quantity=1,
    )

    cart_item3 = CartItem(
        cart_id=cart2.id,
        product_variant_id=samsung_variant.id,
        quantity=2,
    )

    cart_items = [
        cart_item1,
        cart_item2,
        cart_item3,
    ]

    session.add_all(cart_items)

    await session.flush()

    return carts, cart_items


# ==============================================================
# WISHLISTS
# ==============================================================

async def seed_wishlists(session, users, products):
    user1, user2 = users

    (
        legion,
        tuf,
        macbook,
        samsung,
        iphone,
        sony,
        logitech,
    ) = products

    # ----------------------------------------------------------
    # WISHLISTS
    # ----------------------------------------------------------

    wishlist1 = Wishlist(
        user_id=user1.id,
    )

    wishlist2 = Wishlist(
        user_id=user2.id,
    )

    wishlists = [
        wishlist1,
        wishlist2,
    ]

    session.add_all(wishlists)

    await session.flush()

    # ----------------------------------------------------------
    # WISHLIST ITEMS
    # ----------------------------------------------------------

    wishlist_item1 = WishlistItem(
        wishlist_id=wishlist1.id,
        product_id=macbook.id,
    )

    wishlist_item2 = WishlistItem(
        wishlist_id=wishlist1.id,
        product_id=iphone.id,
    )

    wishlist_item3 = WishlistItem(
        wishlist_id=wishlist2.id,
        product_id=legion.id,
    )

    wishlist_items = [
        wishlist_item1,
        wishlist_item2,
        wishlist_item3,
    ]

    session.add_all(wishlist_items)

    await session.flush()

    return wishlists, wishlist_items


# ==============================================================
# ORDERS
# ==============================================================

async def seed_orders(session, users, addresses, variants):
    user1, user2 = users
    address1, address2 = addresses

    (
        legion_variant,
        tuf_variant,
        macbook_variant,
        samsung_variant,
        iphone_variant,
        sony_variant,
        logitech_variant,
    ) = variants

    # ----------------------------------------------------------
    # ORDER 1
    # ----------------------------------------------------------

    order1 = Order(
        user_id=user1.id,
        order_number="ORD-2026-0001",
        status="delivered",
        subtotal=Decimal("74999.00"),
        discount_amount=Decimal("5000.00"),
        shipping_amount=Decimal("0.00"),
        tax_amount=Decimal("8999.00"),
        total_amount=Decimal("83998.00"),
        shipping_address_snapshot={
            "recipient_name": address1.recipient_name,
            "address_line1": address1.address_line1,
            "address_line2": address1.address_line2,
            "city": address1.city,
            "state": address1.state,
            "postal_code": address1.postal_code,
            "country": address1.country,
            "phone": address1.phone,
        },
    )

    # ----------------------------------------------------------
    # ORDER 2
    # ----------------------------------------------------------

    order2 = Order(
        user_id=user2.id,
        order_number="ORD-2026-0002",
        status="shipped",
        subtotal=Decimal("64999.00"),
        discount_amount=Decimal("7000.00"),
        shipping_amount=Decimal("0.00"),
        tax_amount=Decimal("7439.00"),
        total_amount=Decimal("65438.00"),
        shipping_address_snapshot={
            "recipient_name": address2.recipient_name,
            "address_line1": address2.address_line1,
            "address_line2": address2.address_line2,
            "city": address2.city,
            "state": address2.state,
            "postal_code": address2.postal_code,
            "country": address2.country,
            "phone": address2.phone,
        },
    )

    # ----------------------------------------------------------
    # ORDER 3
    # ----------------------------------------------------------

    order3 = Order(
        user_id=user1.id,
        order_number="ORD-2026-0003",
        status="delivered",
        subtotal=Decimal("29999.00"),
        discount_amount=Decimal("3000.00"),
        shipping_amount=Decimal("0.00"),
        tax_amount=Decimal("3239.00"),
        total_amount=Decimal("30238.00"),
        shipping_address_snapshot={
            "recipient_name": address1.recipient_name,
            "address_line1": address1.address_line1,
            "address_line2": address1.address_line2,
            "city": address1.city,
            "state": address1.state,
            "postal_code": address1.postal_code,
            "country": address1.country,
            "phone": address1.phone,
        },
    )

    orders = [
        order1,
        order2,
        order3,
    ]

    session.add_all(orders)

    await session.flush()

    # ----------------------------------------------------------
    # ORDER ITEMS
    # ----------------------------------------------------------

    order_item1 = OrderItem(
        order_id=order1.id,
        product_variant_id=legion_variant.id,
        quantity=1,
        unit_price=Decimal("74999.00"),
        product_name_snapshot="Lenovo Legion 5",
    )

    order_item2 = OrderItem(
        order_id=order2.id,
        product_variant_id=samsung_variant.id,
        quantity=1,
        unit_price=Decimal("64999.00"),
        product_name_snapshot="Samsung Galaxy S24",
    )

    order_item3 = OrderItem(
        order_id=order3.id,
        product_variant_id=sony_variant.id,
        quantity=1,
        unit_price=Decimal("29999.00"),
        product_name_snapshot="Sony WH-1000XM5",
    )

    order_items = [
        order_item1,
        order_item2,
        order_item3,
    ]

    session.add_all(order_items)

    await session.flush()

    return orders, order_items


# ==============================================================
# PAYMENTS
# ==============================================================

async def seed_payments(session, orders):
    order1, order2, order3 = orders

    payment1 = Payment(
        order_id=order1.id,
        amount=Decimal("83998.00"),
        status="completed",
        payment_method="credit_card",
        transaction_reference="TXN-100001",
    )

    payment2 = Payment(
        order_id=order2.id,
        amount=Decimal("65438.00"),
        status="completed",
        payment_method="upi",
        transaction_reference="TXN-100002",
    )

    payment3 = Payment(
        order_id=order3.id,
        amount=Decimal("30238.00"),
        status="completed",
        payment_method="credit_card",
        transaction_reference="TXN-100003",
    )

    payments = [
        payment1,
        payment2,
        payment3,
    ]

    session.add_all(payments)

    await session.flush()

    return payments


# ==============================================================
# SHIPMENTS
# ==============================================================

async def seed_shipments(session, orders, order_items):
    order1, order2, order3 = orders
    order_item1, order_item2, order_item3 = order_items

    # ----------------------------------------------------------
    # SHIPMENT 1
    # ----------------------------------------------------------

    shipment1 = Shipment(
        order_id=order1.id,
        tracking_number="TRK-100001",
        carrier="BlueDart",
        status="delivered",
        shipped_at=datetime(
            2026,
            9,
            18,
            tzinfo=timezone.utc,
        ),
        estimated_delivery_at=datetime(
            2026,
            9,
            21,
            tzinfo=timezone.utc,
        ),
        delivered_at=datetime(
            2026,
            9,
            21,
            tzinfo=timezone.utc,
        ),
    )

    # ----------------------------------------------------------
    # SHIPMENT 2
    # ----------------------------------------------------------

    shipment2 = Shipment(
        order_id=order2.id,
        tracking_number="TRK-100002",
        carrier="Delhivery",
        status="in_transit",
        shipped_at=datetime(
            2026,
            9,
            23,
            tzinfo=timezone.utc,
        ),
        estimated_delivery_at=datetime(
            2026,
            9,
            27,
            tzinfo=timezone.utc,
        ),
        delivered_at=None,
    )

    # ----------------------------------------------------------
    # SHIPMENT 3
    # ----------------------------------------------------------

    shipment3 = Shipment(
        order_id=order3.id,
        tracking_number="TRK-100003",
        carrier="BlueDart",
        status="delivered",
        shipped_at=datetime(
            2026,
            9,
            19,
            tzinfo=timezone.utc,
        ),
        estimated_delivery_at=datetime(
            2026,
            9,
            22,
            tzinfo=timezone.utc,
        ),
        delivered_at=datetime(
            2026,
            9,
            22,
            tzinfo=timezone.utc,
        ),
    )

    shipments = [
        shipment1,
        shipment2,
        shipment3,
    ]

    session.add_all(shipments)

    await session.flush()

    # ----------------------------------------------------------
    # SHIPMENT ITEMS
    # ----------------------------------------------------------

    shipment_item1 = ShipmentItem(
        shipment_id=shipment1.id,
        order_item_id=order_item1.id,
        quantity=1,
    )

    shipment_item2 = ShipmentItem(
        shipment_id=shipment2.id,
        order_item_id=order_item2.id,
        quantity=1,
    )

    shipment_item3 = ShipmentItem(
        shipment_id=shipment3.id,
        order_item_id=order_item3.id,
        quantity=1,
    )

    shipment_items = [
        shipment_item1,
        shipment_item2,
        shipment_item3,
    ]

    session.add_all(shipment_items)

    await session.flush()

    return shipments, shipment_items


# ==============================================================
# RETURNS
# ==============================================================

async def seed_returns(
    session,
    users,
    orders,
    order_items,
):
    user1 = users[0]
    order3 = orders[2]
    order_item3 = order_items[2]

    return_request = Return(
        order_id=order3.id,
        user_id=user1.id,
        status="approved",
        reason="Headphones arrived with physical damage.",
    )

    session.add(return_request)

    await session.flush()

    return_item = ReturnItem(
        return_id=return_request.id,
        order_item_id=order_item3.id,
        quantity=1,
        reason="Physical damage on the headphones.",
        resolution="refund",
    )

    session.add(return_item)

    await session.flush()

    return return_request, return_item


# ==============================================================
# REFUNDS
# ==============================================================

async def seed_refunds(session, return_request):
    refund = Refund(
        return_id=return_request.id,
        amount=Decimal("30238.00"),
        status="completed",
        transaction_reference="REF-100001",
    )

    session.add(refund)

    await session.flush()

    return refund


# ==============================================================
# REVIEWS
# ==============================================================

async def seed_reviews(session, users, products):
    user1, user2 = users

    (
        legion,
        tuf,
        macbook,
        samsung,
        iphone,
        sony,
        logitech,
    ) = products

    review1 = Review(
        user_id=user1.id,
        product_id=legion.id,
        rating=5,
        title="Excellent gaming laptop",
        content=(
            "Excellent performance for gaming and programming. "
            "The RTX 4060 performs very well."
        ),
        verified_purchase=True,
        sentiment="positive",
    )

    review2 = Review(
        user_id=user2.id,
        product_id=samsung.id,
        rating=4,
        title="Great phone",
        content=(
            "Excellent display and camera. "
            "Battery life is good."
        ),
        verified_purchase=True,
        sentiment="positive",
    )

    review3 = Review(
        user_id=user1.id,
        product_id=sony.id,
        rating=2,
        title="Damaged on arrival",
        content=(
            "The headphones arrived with physical damage."
        ),
        verified_purchase=True,
        sentiment="negative",
    )

    reviews = [
        review1,
        review2,
        review3,
    ]

    session.add_all(reviews)

    await session.flush()

    return reviews


# ==============================================================
# PRODUCT DOCUMENT
# ==============================================================

async def seed_product_documents(
    session,
    products,
    variants,
):
    legion = products[0]
    legion_variant = variants[0]

    document = ProductDocument(
        product_id=legion.id,
        variant_id=legion_variant.id,
        file_name="lenovo_legion_5_manual.pdf",
        document_type="manual",
        version="1.0",
        file_path=(
            "documents/products/"
            "lenovo_legion_5_manual.pdf"
        ),
    )

    session.add(document)

    await session.flush()

    chunk1 = DocumentChunk(
        document_id=document.id,
        chunk_index=0,
        content=(
            "Lenovo Legion 5 features an AMD Ryzen 7 "
            "processor and NVIDIA RTX 4060 GPU."
        ),
        chunk_metadata={
            "section": "Specifications",
            "page": 1,
        },
        content_hash="seed-hash-legion-001",
    )

    chunk2 = DocumentChunk(
        document_id=document.id,
        chunk_index=1,
        content=(
            "The laptop includes 16GB RAM and "
            "a 512GB SSD."
        ),
        chunk_metadata={
            "section": "Memory and Storage",
            "page": 2,
        },
        content_hash="seed-hash-legion-002",
    )

    chunks = [
        chunk1,
        chunk2,
    ]

    session.add_all(chunks)

    await session.flush()

    return document, chunks


# ==============================================================
# AUDIT LOGS
# ==============================================================

async def seed_audit_logs(
    session,
    users,
    orders,
    return_request,
):
    user1 = users[0]
    order1 = orders[0]

    audit1 = AuditLog(
        user_id=user1.id,
        action="create",
        entity_type="order",
        entity_id=order1.id,
        old_value=None,
        new_value={
            "order_number": order1.order_number,
            "status": order1.status,
        },
    )

    audit2 = AuditLog(
        user_id=user1.id,
        action="create",
        entity_type="return",
        entity_id=return_request.id,
        old_value=None,
        new_value={
            "status": return_request.status,
            "reason": return_request.reason,
        },
    )

    audit_logs = [
        audit1,
        audit2,
    ]

    session.add_all(audit_logs)

    await session.flush()

    return audit_logs


# ==============================================================
# MAIN SEED FUNCTION
# ==============================================================

async def seed_database():
    async with AsyncSessionLocal() as session:

        try:
            # ======================================================
            # 1. RESET
            # ======================================================

            await reset_database(session)

            # ======================================================
            # 2. USERS
            # ======================================================

            users = await seed_users(session)

            # ======================================================
            # 3. CATEGORIES
            # ======================================================

            categories = await seed_categories(session)

            # ======================================================
            # 4. PRODUCTS
            # ======================================================

            products = await seed_products(
                session,
                categories,
            )

            # ======================================================
            # 5. PRODUCT VARIANTS
            # ======================================================

            variants = await seed_product_variants(
                session,
                products,
            )

            # ======================================================
            # 6. ADDRESSES
            # ======================================================

            addresses = await seed_addresses(
                session,
                users,
            )

            # ======================================================
            # 7. CARTS + CART ITEMS
            # ======================================================

            carts, cart_items = await seed_carts(
                session,
                users,
                variants,
            )

            # ======================================================
            # 8. WISHLISTS + WISHLIST ITEMS
            # ======================================================

            wishlists, wishlist_items = await seed_wishlists(
                session,
                users,
                products,
            )

            # ======================================================
            # 9. ORDERS + ORDER ITEMS
            # ======================================================

            orders, order_items = await seed_orders(
                session,
                users,
                addresses,
                variants,
            )

            # ======================================================
            # 10. PAYMENTS
            # ======================================================

            payments = await seed_payments(
                session,
                orders,
            )

            # ======================================================
            # 11. SHIPMENTS + SHIPMENT ITEMS
            # ======================================================

            shipments, shipment_items = await seed_shipments(
                session,
                orders,
                order_items,
            )

            # ======================================================
            # 12. RETURNS + RETURN ITEMS
            # ======================================================

            return_request, return_item = await seed_returns(
                session,
                users,
                orders,
                order_items,
            )

            # ======================================================
            # 13. REFUND
            # ======================================================

            refund = await seed_refunds(
                session,
                return_request,
            )

            # ======================================================
            # 14. REVIEWS
            # ======================================================

            reviews = await seed_reviews(
                session,
                users,
                products,
            )

            # ======================================================
            # 15. PRODUCT DOCUMENT + CHUNKS
            # ======================================================

            document, chunks = await seed_product_documents(
                session,
                products,
                variants,
            )

            # ======================================================
            # 16. AUDIT LOGS
            # ======================================================

            audit_logs = await seed_audit_logs(
                session,
                users,
                orders,
                return_request,
            )

            # ======================================================
            # 17. COMMIT EVERYTHING
            # ======================================================

            await session.commit()

            # ======================================================
            # SUCCESS OUTPUT
            # ======================================================

            print()
            print("=" * 70)
            print("DATABASE SEED COMPLETED SUCCESSFULLY")
            print("=" * 70)

            print(f"Users:              {len(users)}")
            print(f"Categories:         {len(categories)}")
            print(f"Products:           {len(products)}")
            print(f"Product Variants:   {len(variants)}")
            print(f"Addresses:          {len(addresses)}")
            print(f"Carts:              {len(carts)}")
            print(f"Cart Items:         {len(cart_items)}")
            print(f"Wishlists:          {len(wishlists)}")
            print(f"Wishlist Items:     {len(wishlist_items)}")
            print(f"Orders:             {len(orders)}")
            print(f"Order Items:        {len(order_items)}")
            print(f"Payments:           {len(payments)}")
            print(f"Shipments:          {len(shipments)}")
            print(f"Shipment Items:     {len(shipment_items)}")
            print("Returns:            1")
            print("Return Items:       1")
            print("Refunds:            1")
            print(f"Reviews:            {len(reviews)}")
            print("Product Documents:  1")
            print(f"Document Chunks:    {len(chunks)}")
            print(f"Audit Logs:         {len(audit_logs)}")

            print()
            print("-" * 70)
            print("SEEDED USERS")
            print("-" * 70)

            print()
            print("User 1")
            print("  ID:       1")
            print("  Username: sahil")
            print("  Email:    sahil@example.com")
            print("  Password: password123")

            print()
            print("User 2")
            print("  ID:       2")
            print("  Username: rahul")
            print("  Email:    rahul@example.com")
            print("  Password: password123")

            print()
            print("=" * 70)

        except Exception:
            await session.rollback()
            print()
            print("SEED FAILED")
            print("Transaction rolled back.")
            raise


# ==============================================================
# ENTRY POINT
# ==============================================================

async def main():
    await seed_database()


if __name__ == "__main__":
    asyncio.run(main())
