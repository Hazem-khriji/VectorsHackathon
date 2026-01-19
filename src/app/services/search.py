import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any

load_dotenv()

class SearchService:
    def __init__(self):
        self.qdrant_url = os.getenv('QDRANT_URL', 'http://localhost:6333')
        self.qdrant_api_key = os.getenv('QDRANT_API_KEY')
        self.collection_name = "products"
        
        # Connect to Qdrant
        if self.qdrant_api_key:
            self.client = QdrantClient(url=self.qdrant_url, api_key=self.qdrant_api_key)
        else:
            self.client = QdrantClient(url=self.qdrant_url)
            
        # Load embedding model (lazy loading is better for production but keep it simple here)
        print("🧠 Loading embedding model...")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        print("✅ Model loaded")

    def search_products(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for products using semantic vector search.
        """
        # Convert query to vector
        vector = self.model.encode(query).tolist()
        
        # Search
        response = self.client.query_points(
            collection_name=self.collection_name,
            query=vector,
            limit=limit
        )
        
        results = []
        for point in response.points:
            item = point.payload
            item['score'] = point.score
            results.append(item)
            
        return results

# Singleton instance
search_service = SearchService()
