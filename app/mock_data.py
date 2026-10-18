PRODUCTS = {
    "belt": {
        "id": "belt",
        "name": "Belt",
        "category": "Accessories",
        "description": "A polished leather belt for everyday wear.",
    },
    "shoes": {
        "id": "shoes",
        "name": "Shoes",
        "category": "Footwear",
        "description": "Lightweight sneakers designed for comfort and style.",
    },
    "wallet": {
        "id": "wallet",
        "name": "Wallet",
        "category": "Accessories",
        "description": "Slim leather wallet with multiple card slots.",
    },
    "jacket": {
        "id": "jacket",
        "name": "Jacket",
        "category": "Apparel",
        "description": "Classic outerwear with a warm insulated lining.",
    },
}

PRICES = {
    "belt": 49.99,
    "shoes": 89.50,
    "wallet": 39.00,
    "jacket": 129.99,
}

AVAILABILITY = {
    "belt": {"in_stock": True, "quantity": 25},
    "shoes": {"in_stock": True, "quantity": 14},
    "wallet": {"in_stock": False, "quantity": 0},
    "jacket": {"in_stock": True, "quantity": 8},
}

REVIEWS = {
    "belt": [
        {"comment": "Excellent quality and fits perfectly.", "rating": 5},
        {"comment": "Looks premium and feels durable.", "rating": 4},
    ],
    "shoes": [
        {"comment": "Very comfortable for walking.", "rating": 5},
        {"comment": "Stylish and lightweight.", "rating": 4},
    ],
    "wallet": [
        {"comment": "Good size and neat finish.", "rating": 4},
        {"comment": "A bit thin but useful overall.", "rating": 3},
    ],
    "jacket": [
        {"comment": "Warm and comfortable in cold weather.", "rating": 5},
        {"comment": "Nice design and decent build quality.", "rating": 4},
    ],
}


def get_product(product_id: str):
    return PRODUCTS.get(product_id.lower())


def get_valid_product(product_id: str):
    product = get_product(product_id)
    if product is None:
        raise ValueError(f"Product '{product_id}' not found")
    return product
