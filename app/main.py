from fastapi import FastAPI

from app.routers import availability, catalogue, price, reviews

app = FastAPI(
    title="Ecommerce Mock API",
    description="Mock ecommerce APIs for agentic AI development.",
    version="1.0.0",
)

app.include_router(catalogue.router)
app.include_router(price.router)
app.include_router(availability.router)
app.include_router(reviews.router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
