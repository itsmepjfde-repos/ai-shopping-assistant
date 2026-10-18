from fastapi import APIRouter, HTTPException

from app.data import AVAILABILITY, get_valid_product
from app.models import AvailabilityResponse

router = APIRouter()


@router.get("/availability/{product_id}", response_model=AvailabilityResponse, tags=["availability"])
def get_availability(product_id: str) -> AvailabilityResponse:
    try:
        get_valid_product(product_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    stock = AVAILABILITY[product_id.lower()]
    return AvailabilityResponse(
        product_id=product_id.lower(),
        in_stock=bool(stock["in_stock"]),
        quantity=int(stock["quantity"]),
    )
