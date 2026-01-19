import json
import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer

load_dotenv()

# Configuration
QDRANT_URL = os.getenv('QDRANT_URL', 'http://localhost:6333')
QDRANT_API_KEY = os.getenv('QDRANT_API_KEY')
COLLECTION_NAME = "products"  # Using same collection for simplicity

def connect_qdrant():
    """Connect to Qdrant"""
    print(f"🔗 Connecting to Qdrant...")
    if QDRANT_API_KEY:
        client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
    else:
        client = QdrantClient(url=QDRANT_URL)
    return client

def recreate_collection(client):
    """Recreate Qdrant collection to clear old data"""
    print(f"📦 Recreating collection '{COLLECTION_NAME}'...")
    client.delete_collection(COLLECTION_NAME)
    
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=384,  # all-MiniLM-L6-v2 dimension
            distance=Distance.COSINE
        )
    )
    print("✅ Collection recreated!")

def load_embedding_model():
    print("🧠 Loading embedding model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    return model

def upload_products(client, model, products):
    print(f"\n📤 Uploading {len(products)} scraped products...")
    
    points = []
    
    for idx, product in enumerate(products):
        # Create text for embedding
        text = f"{product['title']} {product['description']}"
        
        # Generate vector
        vector = model.encode(text).tolist()
        
        # Create point (using integer ID for simplicity if possible, but UUID requires string ID support or hashing)
        # Qdrant supports both integer and UUID strings.
        # Since we generated UUIDs in scraper, we can use them directly or hash them.
        # For simplicity in this script, we'll let Qdrant handle UUID strings if supported or map to integers.
        # However, typically integer IDs are faster. Let's use the index or hash.
        # But wait, Qdrant Python client PointStruct 'id' can be int or str (UUID).
        
        point = PointStruct(
            id=product['id'],  # UUID string from scraper
            vector=vector,
            payload=product
        )
        
        points.append(point)
        
        if (idx + 1) % 20 == 0:
            print(f"  Processed {idx + 1}/{len(products)}...")
    
    # Upload batch
    batch_size = 100
    for i in range(0, len(points), batch_size):
        batch = points[i:i+batch_size]
        client.upsert(
            collection_name=COLLECTION_NAME,
            points=batch
        )
    
    print(f"✅ Uploaded {len(points)} products!")

def main():
    # Load scraped products
    input_file = 'data/raw/scraped_products.json'
    if not os.path.exists(input_file):
        print(f"❌ File not found: {input_file}")
        return

    print("📂 Loading scraped products...")
    with open(input_file, 'r') as f:
        products = json.load(f)
    print(f"✅ Loaded {len(products)} products")
    
    client = connect_qdrant()
    recreate_collection(client)
    model = load_embedding_model()
    upload_products(client, model, products)
    
    print("\n🎉 PHASE 2 UPLOAD COMPLETE!")

if __name__ == "__main__":
    main()
