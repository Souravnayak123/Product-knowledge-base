from fastapi import FastAPI, HTTPException

from .database import product_collection, create_indexes
from .routes.products import router as product_router

app = FastAPI(
    title="Product Knowledge Base API",
    description="Product and shelf-life management using MongoDB",
    version="1.1.0",
)


@app.on_event("startup")
def startup_event():
    create_indexes()


@app.get("/")
def root():
    return {"message": "Product Knowledge Base API is running"}


@app.get("/health")
def health_check():
    try:
        product_collection.database.client.admin.command("ping")
        return {"status": "healthy", "mongodb": "connected"}
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"MongoDB connection failed: {exc}",
        )


app.include_router(product_router)
