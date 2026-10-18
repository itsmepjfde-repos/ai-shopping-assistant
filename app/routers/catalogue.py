from fastapi import APIRouter

from app.data import PRODUCTS
from app.models import Product

router = APIRouter()


@router.get("/products", response_model=list[Product], tags=["catalogue"])
def get_products() -> list[Product]:
    return [Product(**product) for product in PRODUCTS.values()]
