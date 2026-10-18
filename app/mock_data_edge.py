"""Deterministic edge-case fixtures for testing the ecommerce assistant."""

PRODUCTS = {
    "jacket-black-leather": {
        "id": "jacket-black-leather",
        "name": "Black Leather Jacket",
        "category": "Apparel",
        "description": "A black genuine leather jacket with a warm insulated lining.",
    },
    "jacket-black-faux": {
        "id": "jacket-black-faux",
        "name": "Black Faux-Leather Jacket",
        "category": "Apparel",
        "description": "A black jacket made from faux leather with a lightweight lining.",
    },
    "jacket-brown-leather": {
        "id": "jacket-brown-leather",
        "name": "Classic Leather Jacket",
        "category": "Apparel",
        "description": "A brown genuine leather jacket with a simple classic design.",
    },
    "jacket-generic": {
        "id": "jacket-generic",
        "name": "Everyday Jacket",
        "category": "Apparel",
        "description": "A versatile jacket for everyday wear.",
    },
    "shoes-black": {
        "id": "shoes-black",
        "name": "Black Walking Shoes",
        "category": "Footwear",
        "description": "Black lightweight shoes designed for comfortable walking.",
    },
    "shoes-blue": {
        "id": "shoes-blue",
        "name": "Blue Running Shoes",
        "category": "Footwear",
        "description": "Blue running shoes with a cushioned sole.",
    },
    "wallet-slim": {
        "id": "wallet-slim",
        "name": "Slim Leather Wallet",
        "category": "Accessories",
        "description": "A slim genuine leather wallet with multiple card slots.",
    },
    "wallet-generic": {
        "id": "wallet-generic",
        "name": "Everyday Wallet",
        "category": "Accessories",
        "description": "A compact wallet for daily use.",
    },
    "belt-budget-exact": {
        "id": "belt-budget-exact",
        "name": "Leather Belt",
        "category": "Accessories",
        "description": "A black leather belt with a simple metal buckle.",
    },
    "belt-budget-over": {
        "id": "belt-budget-over",
        "name": "Premium Leather Belt",
        "category": "Accessories",
        "description": "A black premium leather belt with a polished metal buckle.",
    },
}

PRICES = {
    "jacket-black-leather": 100.00,
    "jacket-black-faux": 99.99,
    "jacket-brown-leather": 100.01,
    "jacket-generic": 75.00,
    "shoes-black": 0.01,
    "shoes-blue": 250.00,
    "wallet-slim": 39.00,
    "wallet-generic": 32.00,
    "belt-budget-exact": 50.00,
    "belt-budget-over": 50.01,
}

AVAILABILITY = {
    "jacket-black-leather": {"in_stock": True, "quantity": 1},
    "jacket-black-faux": {"in_stock": True, "quantity": 12},
    "jacket-brown-leather": {"in_stock": False, "quantity": 0},
    "jacket-generic": {"in_stock": False, "quantity": 4},
    "shoes-black": {"in_stock": True, "quantity": 3},
    "shoes-blue": {"in_stock": True, "quantity": 0},
    "wallet-slim": {"in_stock": True, "quantity": 1},
    "wallet-generic": {"in_stock": True, "quantity": 4},
    "belt-budget-exact": {"in_stock": True, "quantity": 5},
    "belt-budget-over": {"in_stock": True, "quantity": 5},
}

REVIEWS = {
    "jacket-black-leather": [
        {"comment": "Excellent quality and very warm.", "rating": 5},
        {"comment": "The leather feels durable.", "rating": 4},
    ],
    "jacket-black-faux": [
        {"comment": "Looks good for the price.", "rating": 4},
        {"comment": "The lining is thinner than expected.", "rating": 3},
    ],
    "jacket-brown-leather": [
        {"comment": "Poor stitching and disappointing finish.", "rating": 2},
        {"comment": "Not as durable as expected.", "rating": 3},
    ],
    "jacket-generic": [
        {"comment": "Average quality.", "rating": 3.45},
    ],
    "shoes-black": [
        {"comment": "Comfortable for walking.", "rating": 4},
    ],
    "shoes-blue": [
        {"comment": "Excellent cushioning.", "rating": 5},
        {"comment": "Very comfortable.", "rating": 4},
        {"comment": "Great for long runs.", "rating": 5},
    ],
    "wallet-slim": [
        {"comment": "Good finish and useful card slots.", "rating": 4},
        {"comment": "A little smaller than expected.", "rating": 3},
    ],
    "wallet-generic": [
        {"comment": "Very disappointing quality.", "rating": 1},
        {"comment": "Would not buy again.", "rating": 2},
    ],
    "belt-budget-exact": [
        {"comment": "Exactly what I needed.", "rating": 4},
    ],
    "belt-budget-over": [
        {"comment": "Excellent leather and buckle.", "rating": 5},
    ],
}


def get_product(product_id: str):
    return PRODUCTS.get(product_id.lower())


def get_valid_product(product_id: str):
    product = get_product(product_id)
    if product is None:
        raise ValueError(f"Product '{product_id}' not found")
    return product
