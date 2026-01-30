import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient, models

def create_behavioral_index():
    # Load environment variables
    load_dotenv()

    # Initialize Qdrant Client
    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_api_key = os.getenv("QDRANT_API_KEY")

    if not qdrant_url or not qdrant_api_key:
        print("Error: QDRANT_URL and QDRANT_API_KEY must be set in .env file")
        return

    client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)

    collection_name = "user_behaviors"

    print(f"Connecting to Qdrant Cloud: {qdrant_url}")

    # Ensure collection exists
    if not client.collection_exists(collection_name):
        print(f"Collection '{collection_name}' does not exist yet. It will be created on first value tracking.")
        # We can create it now to be safe and ensure index is there
        print(f"Creating collection '{collection_name}'...")
        try:
            from qdrant_client.http.models import Distance, VectorParams
            client.create_collection(
                collection_name=collection_name,
                vectors_config={
                    "behavior": VectorParams(
                        size=384,  # all-MiniLM-L6-v2 output size
                        distance=Distance.COSINE
                    )
                }
            )
            print(f"Created collection '{collection_name}'")
        except Exception as e:
            print(f"Error creating collection: {e}")

    # Create Index for session_id (Keyword)
    print("Creating index for 'session_id'...")
    try:
        client.create_payload_index(
            collection_name=collection_name,
            field_name="session_id",
            field_schema=models.PayloadSchemaType.KEYWORD,
        )
        print("Successfully created index for 'session_id'")
    except Exception as e:
        print(f"Failed to create index (might already exist): {e}")

    # Create Index for event_type (Keyword)
    print("Creating index for 'event_type'...")
    try:
        client.create_payload_index(
            collection_name=collection_name,
            field_name="event_type",
            field_schema=models.PayloadSchemaType.KEYWORD,
        )
        print("Successfully created index for 'event_type'")
    except Exception as e:
        print(f"Failed to create index (might already exist): {e}")

    print("Index creation complete!")

if __name__ == "__main__":
    create_behavioral_index()
