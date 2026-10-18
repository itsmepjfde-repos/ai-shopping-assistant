from typing import List

from pydantic import BaseModel, Field


class Product(BaseModel):
    id: str
    name: str
    category: str
    description: str


class PriceResponse(BaseModel):
    product_id: str
    price: float
    currency: str = "USD"


class AvailabilityResponse(BaseModel):
    product_id: str
    in_stock: bool
    quantity: int


class ReviewComment(BaseModel):
    comment: str
    rating: int = Field(..., ge=1, le=5)


class ReviewResponse(BaseModel):
    product_id: str
    reviews: List[ReviewComment]
    rating: float = Field(..., ge=1, le=5)
