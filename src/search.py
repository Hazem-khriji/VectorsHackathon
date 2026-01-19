import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

load_dotenv()

QDRANT_URL = os.getenv('QDRANT_URL', 'http://localhost:6333')
QDRANT_API_KEY = os.getenv('QDRANT_API_KEY')
COLLECTION_NAME = "products"

class SearchEngine:
    def __init__(self):
        # Connect to Qdrant
        if QDRANT_API_KEY:
            self.client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
        else:
            self.client = QdrantClient(url=QDRANT_URL)
        
        # Load model
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        print("✅ Search engine ready!\n")
    
    def search(self, query, limit=5):
        """Search for products"""
        print(f"🔍 Searching for: '{query}'\n")
        
        # Convert query to vector
        vector = self.model.encode(query).tolist()
        
        # Search
        response = self.client.query_points(
            collection_name=COLLECTION_NAME,
            query=vector,
            limit=limit
        )
        
        return response.points
    
    def display(self, results):
        """Display results nicely"""
        if not results:
            print("No results found.")
            return
        
        print("=" * 60)
        for i, hit in enumerate(results, 1):
            p = hit.payload
            score = hit.score
            
            print(f"\n{i}. {p['title']}")
            print(f"   💰 Price: ${p['price']:.2f}")
            print(f"   📂 Category: {p['category']}")
            print(f"   ⭐ Rating: {p['rating']:.1f}/5")
            print(f"   🎯 Match: {score:.2%}")
            print(f"   📝 {p['description'][:80]}...")
        
        print("\n" + "=" * 60 + "\n")

def main():
    print("🚀 FinCommerce Search Engine - Phase 1\n")
    
    engine = SearchEngine()
    
    # Demo searches
    queries = ["laptop", "phone", "perfume"]
    
    for query in queries:
        results = engine.search(query, limit=3)
        engine.display(results)
        input("Press Enter for next search...\n")
    
    # Interactive mode
    print("💡 Try your own searches! (type 'exit' to quit)\n")
    
    while True:
        query = input("🔍 Search: ").strip()
        
        if query.lower() in ['exit', 'quit', 'q']:
            print("👋 Goodbye!")
            break
        
        if query:
            results = engine.search(query)
            engine.display(results)

if __name__ == "__main__":
    main()