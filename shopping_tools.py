"""LangChain tools backed by the local ecommerce API."""

import json
import os
import re
from typing import Any

import requests
from langchain_core.tools import tool
from pydantic import BaseModel, Field

API_BASE_URL = os.getenv("ECOMM_API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
REQUEST_TIMEOUT_SECONDS = 10


class CatalogSearchInput(BaseModel):
    query: str = Field(description="Shopper's product search criteria.")


class ProductIdInput(BaseModel):
    product_id: str = Field(description="Product ID returned by CatalogSearch.")


def _get_api_json(path: str) -> Any:
    response = requests.get(
        f"{API_BASE_URL}{path}",
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return response.json()


@tool("CatalogSearch", args_schema=CatalogSearchInput)
def catalog_search(query: str) -> str:
    """Find catalogue products matching the query; returns id, name, category, and description."""
    products = _get_api_json("/products")
    terms = {
        term.lower()
        for term in re.findall(r"[a-zA-Z]+", query)
        if term.lower() not in {"a", "an", "and", "for", "in", "of", "the", "to", "under", "below", "less", "than", "with"}
    }

    def relevance(product: dict[str, Any]) -> int:
        searchable_text = " ".join(
            str(product.get(field, ""))
            for field in ("name", "category", "description")
        ).lower()
        return sum(term in searchable_text for term in terms)

    ranked_products = sorted(products, key=relevance, reverse=True)
    matching_products = [product for product in ranked_products if relevance(product) > 0]
    return json.dumps(matching_products if terms else ranked_products)


@tool("PricingAPI", args_schema=ProductIdInput)
def pricing_api(product_id: str) -> str:
    """Get a product's price and discount status."""
    price = _get_api_json(f"/price/{product_id}")
    price["discount"] = "No discount"
    return json.dumps(price)


@tool("InventoryAPI", args_schema=ProductIdInput)
def inventory_api(product_id: str) -> str:
    """Get a product's stock availability and quantity."""
    return json.dumps(_get_api_json(f"/availability/{product_id}"))


@tool("ReviewAPI", args_schema=ProductIdInput)
def review_api(product_id: str) -> str:
    """Get a product's average rating, review count, and sentiment."""
    reviews = _get_api_json(f"/reviews/{product_id}")
    average_rating = reviews["rating"]
    if average_rating >= 4:
        sentiment = "positive"
    elif average_rating >= 3:
        sentiment = "mixed"
    else:
        sentiment = "negative"

    return json.dumps(
        {
            "product_id": reviews["product_id"],
            "average_rating": average_rating,
            "review_count": len(reviews["reviews"]),
            "sentiment": sentiment,
        }
    )


SHOPPING_TOOLS = [catalog_search, pricing_api, inventory_api, review_api]
