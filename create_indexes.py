import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient, models

def create_product_index():
    # Load environment variables
    load_dotenv()

    # Initialize Qdrant Client
    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_api_key = os.getenv("QDRANT_API_KEY")

    if not qdrant_url or not qdrant_api_key:
        print("Error: QDRANT_URL and QDRANT_API_KEY must be set in .env file")
        return

    client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)

    collection_name = "products"

    print(f"Connecting to Qdrant Cloud: {qdrant_url}")

    # Create Index for discounted_price (Float)
    print("Creating index for 'discounted_price'...")
    try:
        client.create_payload_index(
            collection_name=collection_name,
            field_name="discounted_price",
            field_schema=models.PayloadSchemaType.FLOAT,
        )
        print("Successfully created index for 'discounted_price'")
    except Exception as e:
        print(f"Failed to create index (might already exist): {e}")

    # Create Index for actual_price (Float)
    print("Creating index for 'actual_price'...")
    try:
        client.create_payload_index(
            collection_name=collection_name,
            field_name="actual_price",
            field_schema=models.PayloadSchemaType.FLOAT,
        )
        print("Successfully created index for 'actual_price'")
    except Exception as e:
        print(f"Failed to create index (might already exist): {e}")

    # Create Index for rating (Float)
    print("Creating index for 'rating'...")
    try:
        client.create_payload_index(
            collection_name=collection_name,
            field_name="rating",
            field_schema=models.PayloadSchemaType.FLOAT,
        )
        print("Successfully created index for 'rating'")
    except Exception as e:
        print(f"Failed to create index (might already exist): {e}")

    # Create Index for category (Keyword)
    print("Creating index for 'category'...")
    try:
        client.create_payload_index(
            collection_name=collection_name,
            field_name="category",
            field_schema=models.PayloadSchemaType.KEYWORD,
        )
        print("Successfully created index for 'category'")
    except Exception as e:
        print(f"Failed to create index (might already exist): {e}")

    print("Index creation complete!")

if __name__ == "__main__":
    create_product_index()
