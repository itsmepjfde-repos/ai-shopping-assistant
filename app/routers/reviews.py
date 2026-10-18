from fastapi import APIRouter, HTTPException

from app.data import REVIEWS, get_valid_product
from app.models import ReviewComment, ReviewResponse

router = APIRouter()


@router.get("/reviews/{product_id}", response_model=ReviewResponse, tags=["reviews"])
def get_reviews(product_id: str) -> ReviewResponse:
    try:
        get_valid_product(product_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    product_reviews = REVIEWS[product_id.lower()]
    comments = [ReviewComment(**review) for review in product_reviews]
    average_rating = round(sum(item.rating for item in comments) / len(comments), 2)

    return ReviewResponse(
        product_id=product_id.lower(),
        reviews=comments,
        rating=average_rating,
    )
