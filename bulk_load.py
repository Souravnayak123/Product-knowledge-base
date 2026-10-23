import json

from pymongo.errors import BulkWriteError, PyMongoError

from app.database import product_collection, create_indexes
from app.models import ProductShelfLifeRequest
from app.services.product_service import prepare_product_document


def load_products():
    create_indexes()

    with open("data/products.json", "r", encoding="utf-8") as file:
        products = json.load(file)

    documents = []
    skipped = 0

    for index, product in enumerate(products):
        try:
            validated_product = ProductShelfLifeRequest(**product)
            documents.append(prepare_product_document(validated_product))
        except (ValueError, TypeError) as exc:
            skipped += 1
            print(f"Skipping record {index}: {exc}")

    if not documents:
        print("No valid products to insert.")
        return

    try:
        result = product_collection.insert_many(
            documents,
            ordered=False,
        )
        print(
            f"Inserted {len(result.inserted_ids)} products. "
            f"Skipped {skipped} invalid records."
        )
    except BulkWriteError as exc:
        print(
            "Bulk insert completed with duplicate/database errors: "
            f"{exc.details}"
        )
    except PyMongoError as exc:
        print(f"MongoDB operation failed: {exc}")


if __name__ == "__main__":
    load_products()
