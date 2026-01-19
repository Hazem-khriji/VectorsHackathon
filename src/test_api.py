import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def test_search(query, user_id=None):
    """Test search with optional user context"""
    print(f"\n🔎 Searching for '{query}'" + (f" with User ID {user_id}..." if user_id else "..."))
    
    try:
        params = {"q": query}
        if user_id:
            params["user_id"] = user_id
            
        response = requests.get(f"{BASE_URL}/search", params=params)
        data = response.json()
        
        if response.status_code != 200:
            print(f"❌ Error: {response.status_code}")
            return

        # Show Context
        context = data.get('user_context')
        if context:
            print(f"👤 User: {context['username']} | 💰 Balance: ${context['balance']} | 📉 Budget: ${context['budget']}")
        
        # Show Results
        results = data.get('results', [])
        print(f"\n✅ Found {len(results)} results:")
        print("-" * 50)
        for i, item in enumerate(results[:5], 1): # Show top 5
            print(f"{i}. {item['title']}")
            print(f"   💵 ${item['price']} | 📂 {item['category']}")
        print("-" * 50)
        
    except Exception as e:
        print(f"❌ Request Failed: {e}")

if __name__ == "__main__":
    print(f"🚀 FinCommerce Interactive Tester ({BASE_URL})\n")
    
    while True:
        try:
            query = input("❓ Enter search query (or 'exit'): ").strip()
            if query.lower() == 'exit':
                break
            if not query:
                continue
                
            use_user = input("👤 Use demo user? (y/n): ").strip().lower()
            user_id = 1 if use_user == 'y' else None
            
            test_search(query, user_id)
            print("\n")
            
        except KeyboardInterrupt:
            break
            
    print("\n👋 Bye!")
