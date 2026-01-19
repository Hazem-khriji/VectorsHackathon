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
COLLECTION_NAME = "products"

def connect_qdrant():
    """Connect to Qdrant"""
    print(f"🔗 Connecting to Qdrant...")
    
    if QDRANT_API_KEY:
        client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
    else:
        client = QdrantClient(url=QDRANT_URL)
    
    print("✅ Connected!")
    return client

def create_collection(client):
    """Create Qdrant collection"""
    print(f"📦 Creating collection '{COLLECTION_NAME}'...")
    
    # Delete if exists
    try:
        client.delete_collection(COLLECTION_NAME)
        print("  (Deleted old collection)")
    except:
        pass
    
    # Create new
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=384,  # all-MiniLM-L6-v2 dimension
            distance=Distance.COSINE
        )
    )
    print("✅ Collection created!")

def load_embedding_model():
    """Load sentence transformer model"""
    print("🧠 Loading embedding model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print("✅ Model loaded!")
    return model

def upload_products(client, model, products):
    """Upload products to Qdrant"""
    print(f"\n📤 Uploading {len(products)} products...")
    
    points = []
    
    for idx, product in enumerate(products):
        # Create text for embedding
        text = f"{product['title']} {product['description']}"
        
        # Generate vector
        vector = model.encode(text).tolist()
        
        # Create point
        point = PointStruct(
            id=idx,
            vector=vector,
            payload={
                'product_id': product['id'],
                'title': product['title'],
                'description': product['description'],
                'price': product['price'],
                'category': product['category'],
                'rating': product['rating'],
                'image': product['image']
            }
        )
        
        points.append(point)
        
        # Progress
        if (idx + 1) % 20 == 0:
            print(f"  Processed {idx + 1}/{len(products)}...")
    
    # Upload all at once
    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )
    
    print(f"✅ Uploaded {len(points)} products!")

def main():
    # Load products
    print("📂 Loading products...")
    with open('data/raw/products.json', 'r') as f:
        products = json.load(f)
    print(f"✅ Loaded {len(products)} products")
    
    # Connect to Qdrant
    client = connect_qdrant()
    
    # Create collection
    create_collection(client)
    
    # Load model
    model = load_embedding_model()
    
    # Upload
    upload_products(client, model, products)
    
    print("\n🎉 PHASE 1 UPLOAD COMPLETE!")
    print(f"   Products in Qdrant: {len(products)}")
    print(f"   Collection: {COLLECTION_NAME}")

if __name__ == "__main__":
    main()