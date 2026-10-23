import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
DATABASE_NAME = os.getenv("DATABASE_NAME", "product_knowledge_base")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "product_shelf_life")

client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
db = client[DATABASE_NAME]
product_collection = db[COLLECTION_NAME]


def create_indexes():
    product_collection.create_index(
        [
            ("ean", 1),
            ("batch_no", 1),
            ("mfg_date", 1),
        ],
        unique=True,
        name="unique_product_batch",
    )
