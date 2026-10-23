from datetime import datetime, timezone

from app.models import ProductShelfLifeRequest


def prepare_product_document(product: ProductShelfLifeRequest) -> dict:
    """Validate shelf life and convert an API model into a MongoDB document."""
    mfg_date = datetime.strptime(
        product.mfg_date, "%Y-%m-%d"
    ).replace(tzinfo=timezone.utc)

    exp_date = datetime.strptime(
        product.exp_date, "%Y-%m-%d"
    ).replace(tzinfo=timezone.utc)

    if exp_date <= mfg_date:
        raise ValueError("exp_date must be greater than mfg_date")

    calculated_shelf_life = (exp_date - mfg_date).days

    if product.shelf_life_days != calculated_shelf_life:
        raise ValueError(
            f"shelf_life_days does not match mfg_date and exp_date. "
            f"Provided: {product.shelf_life_days}, "
            f"calculated: {calculated_shelf_life}"
        )

    now = datetime.now(timezone.utc)

    return {
        "ean": product.ean,
        "product_name": product.product_name,
        "product_category": product.product_category,
        "mrp": product.mrp,
        "batch_no": product.batch_no,
        "mfg_date": mfg_date,
        "exp_date": exp_date,
        "shelf_life_days": calculated_shelf_life,
        "shelf_life_basis": product.shelf_life_basis,
        "storage_conditions": product.storage_conditions,
        "packaging_type": product.packaging_type,
        "source": product.source,
        "remarks": product.remarks,
        "created_at": now,
        "updated_at": now,
    }
