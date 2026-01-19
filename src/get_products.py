import requests
import json

def fetch_products(limit=100):
    """Fetch products from DummyJSON API"""
    
    print(f"🔍 Fetching {limit} products...")
    
    url = f"https://dummyjson.com/products?limit={limit}"
    response = requests.get(url)
    data = response.json()
    
    products = []
    for p in data['products']:
        product = {
            'id': str(p['id']),
            'title': p['title'],
            'description': p['description'],
            'price': float(p['price']),
            'category': p['category'],
            'image': p.get('thumbnail', ''),
            'rating': float(p.get('rating', 0))
        }
        products.append(product)
    
    print(f"✅ Got {len(products)} products")
    return products

def save_products(products, filename='data/raw/products.json'):
    """Save products to JSON file"""
    
    with open(filename, 'w') as f:
        json.dump(products, f, indent=2)
    
    print(f"💾 Saved to {filename}")

if __name__ == "__main__":
    # Fetch 100 products
    products = fetch_products(100)
    
    # Save
    save_products(products)
    
    # Show sample
    print("\n📦 Sample product:")
    print(f"Title: {products[0]['title']}")
    print(f"Price: ${products[0]['price']}")
    print(f"Category: {products[0]['category']}")