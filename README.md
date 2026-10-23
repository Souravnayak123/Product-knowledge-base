# Product Knowledge Base

Local MongoDB + FastAPI implementation for product and shelf-life management.

## Project structure

```text
product-knowledge-base/
├── app/
│   ├── __init__.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   ├── routes/
│   │   ├── __init__.py
│   │   └── products.py
│   └── services/
│       ├── __init__.py
│       └── product_service.py
├── data/
│   └── products.json
├── .env
├── bulk_load.py
├── README.md
└── requirements.txt
```

## 1. Requirements

- MongoDB Community Server running locally
- Python 3.10+
- pip

## 2. Install

```bash
pip install -r requirements.txt
```

## 3. Start MongoDB

Make sure the MongoDB Community Server service is running.

Default connection:

```text
mongodb://localhost:27017/
```

## 4. Start API

From this project folder:

```bash
uvicorn app.main:app --reload
```

Open Swagger UI:

```text
http://127.0.0.1:8000/docs
```

## 5. Single product API

Endpoint:

```text
POST /knowledge-base/shelf-life
```

Request body:

```json
{
  "ean": "8901234567890",
  "product_name": "Packaged Milk",
  "product_category": "Dairy",
  "mrp": 30.0,
  "batch_no": "BATCH123",
  "mfg_date": "2026-10-01",
  "exp_date": "2026-10-08",
  "shelf_life_days": 7,
  "shelf_life_basis": "From manufacturing date",
  "storage_conditions": "Refrigerated",
  "packaging_type": "Sealed",
  "source": "Product label",
  "remarks": "Store under refrigeration"
}
```

The single-product API validates the dates and shelf life and then creates or updates the product batch using the unique key:

```text
ean + batch_no + mfg_date
```

## 6. Multiple product API

Endpoint:

```text
POST /knowledge-base/shelf-life/bulk
```

Send an array of products:

```json
[
  {
    "ean": "8901234567890",
    "product_name": "Packaged Milk",
    "product_category": "Dairy",
    "mrp": 30.0,
    "batch_no": "BATCH123",
    "mfg_date": "2026-10-01",
    "exp_date": "2026-10-08",
    "shelf_life_days": 7,
    "shelf_life_basis": "From manufacturing date",
    "storage_conditions": "Refrigerated",
    "packaging_type": "Sealed",
    "source": "Product label",
    "remarks": "Store under refrigeration"
  },
  {
    "ean": "8901234567891",
    "product_name": "Campa Cola",
    "product_category": "Soft Drink",
    "mrp": 40.0,
    "batch_no": "BATCH124",
    "mfg_date": "2026-10-01",
    "exp_date": "2027-10-01",
    "shelf_life_days": 365,
    "shelf_life_basis": "From manufacturing date",
    "storage_conditions": "Store in a cool and dry place",
    "packaging_type": "PET Bottle",
    "source": "Product label",
    "remarks": null
  }
]
```

The bulk API:

1. Validates every product.
2. Checks `exp_date > mfg_date`.
3. Calculates shelf life.
4. Checks the provided shelf life.
5. Inserts all valid records using MongoDB `insert_many()`.

If any record fails validation, the API returns `400` and does not perform the bulk insert.

## 7. MongoDB

Database:

```text
product_knowledge_base
```

Collection:

```text
product_shelf_life
```

The API stores dates and timestamps as BSON datetime values.

A unique index uses:

```text
ean + batch_no + mfg_date
```

to prevent duplicate product batches.

## 8. Optional JSON bulk loader

The existing `bulk_load.py` can still be used to load verified test data from:

```text
data/products.json
```

Run:

```bash
python bulk_load.py
```

The script now uses the same validation logic as the APIs.

Do not invent missing manufacturing dates, expiry dates, or shelf-life values. Only load verified product information.
