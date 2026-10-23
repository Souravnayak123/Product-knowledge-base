from fastapi import APIRouter, HTTPException
from pymongo.errors import BulkWriteError, PyMongoError

from ..database import product_collection
from ..models import ProductShelfLifeRequest
from ..services.product_service import prepare_product_document

router = APIRouter(
    prefix="/knowledge-base/shelf-life",
    tags=["Product Shelf Life"],
)


@router.post("")
def create_or_update_product(product: ProductShelfLifeRequest):
    """Create or update one product batch."""
    try:
        document = prepare_product_document(product)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    try:
        document_without_created_at = {
    key: value
    for key, value in document.items()
    if key != "created_at"
}

result = product_collection.update_one(
    {
        "ean": product.ean,
        "batch_no": product.batch_no,
        "mfg_date": document["mfg_date"],
    },
    {
        "$set": document_without_created_at,
        "$setOnInsert": {
            "created_at": document["created_at"]
        },
    },
    upsert=True,
)
    except PyMongoError as exc:
        raise HTTPException(
            status_code=500,
            detail=f"MongoDB operation failed: {exc}",
        )

    if result.upserted_id:
        return {
            "status": "created",
            "message": "Product batch inserted successfully",
            "id": str(result.upserted_id),
            "shelf_life_days": document["shelf_life_days"],
        }

    return {
        "status": "updated",
        "message": "Product batch updated successfully",
        "matched_count": result.matched_count,
        "modified_count": result.modified_count,
        "shelf_life_days": document["shelf_life_days"],
    }


@router.post("/bulk")
def create_products_bulk(products: list[ProductShelfLifeRequest]):
    """Create multiple product batches in one request."""
    if not products:
        raise HTTPException(
            status_code=400,
            detail="Request must contain at least one product",
        )

    documents = []
    invalid_products = []

    for index, product in enumerate(products):
        try:
            documents.append(prepare_product_document(product))
        except ValueError as exc:
            invalid_products.append({
                "index": index,
                "ean": product.ean,
                "batch_no": product.batch_no,
                "error": str(exc),
            })

    if invalid_products:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "One or more products failed validation",
                "invalid_products": invalid_products,
            },
        )

    try:
        result = product_collection.insert_many(
            documents,
            ordered=False,
        )
    except BulkWriteError as exc:
        details = exc.details or {}
        write_errors = details.get("writeErrors", [])

        raise HTTPException(
            status_code=409,
            detail={
                "message": (
                    "Bulk insert encountered database errors. "
                    "Some records may already have been inserted."
                ),
                "write_error_count": len(write_errors),
                "write_errors": [
                    {
                        "index": error.get("index"),
                        "code": error.get("code"),
                        "message": error.get("errmsg"),
                    }
                    for error in write_errors
                ],
            },
        )
    except PyMongoError as exc:
        raise HTTPException(
            status_code=500,
            detail=f"MongoDB bulk insert failed: {exc}",
        )

    return {
        "status": "created",
        "message": "Products inserted successfully",
        "requested_count": len(products),
        "inserted_count": len(result.inserted_ids),
        "ids": [str(product_id) for product_id in result.inserted_ids],
    }
