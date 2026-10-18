from fastapi import APIRouter, HTTPException

from app.data import PRICES, get_valid_product
from app.models import PriceResponse

router = APIRouter()


@router.get("/price/{product_id}", response_model=PriceResponse, tags=["price"])
def get_price(product_id: str) -> PriceResponse:
    try:
        get_valid_product(product_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return PriceResponse(
        product_id=product_id.lower(),
        price=float(PRICES[product_id.lower()]),
        currency="USD",
    )
