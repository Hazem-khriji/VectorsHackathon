import requests
from bs4 import BeautifulSoup
import json
import time
import random
import uuid
import os

CATEGORIES = {
    "laptops": "https://webscraper.io/test-sites/e-commerce/allinone/computers/laptops",
    "tablets": "https://webscraper.io/test-sites/e-commerce/allinone/computers/tablets",
    "phones": "https://webscraper.io/test-sites/e-commerce/allinone/phones/touch"
}

def scrape_category(category_name, url):
    print(f"🕵️  Scraping {category_name}: {url}")
    
    products = []
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        items = soup.find_all('div', class_='thumbnail')
        print(f"🧩 Found {len(items)} items in {category_name}.")
        
        for item in items:
            try:
                # Title
                title_tag = item.find('a', class_='title')
                title = title_tag['title'] if title_tag else item.find('a', class_='title').text.strip()
                
                # Price
                price_tag = item.find('h4', class_='price')
                price_str = price_tag.text.strip().replace('$', '')
                price = float(price_str)
                
                # Description
                description = item.find('p', class_='description').text.strip()
                
                # Rating
                rating_stars = item.find_all('span', class_='glyphicon-star')
                rating = float(len(rating_stars))
                
                # Image
                img_tag = item.find('img', class_='img-responsive')
                image_url = img_tag['src']
                if not image_url.startswith('http'):
                    image_url = f"https://webscraper.io{image_url}"
                
                product = {
                    "id": str(uuid.uuid4()),
                    "title": title,
                    "price": price,
                    "description": description,
                    "category": category_name,
                    "rating": rating,
                    "image": image_url,
                    "source": "webscraper.io"
                }
                products.append(product)
                
            except Exception as e:
                print(f"⚠️ Error parsing item: {e}")
                continue
        
        return products
        
    except Exception as e:
        print(f"❌ Failed to scrape {category_name}: {e}")
        return []

def save_products(products):
    output_dir = 'data/raw'
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'scraped_products.json')
    
    with open(output_path, 'w') as f:
        json.dump(products, f, indent=4)
    
    print(f"💾 Saved {len(products)} products to {output_path}")

def main():
    print("🚀 Starting FinCommerce Multi-Category Scraper...")
    all_products = []
    
    for category, url in CATEGORIES.items():
        products = scrape_category(category, url)
        all_products.extend(products)
        time.sleep(1) # Be polite
    
    print(f"✅ Total products scraped: {len(all_products)}")
    
    if all_products:
        save_products(all_products)
    else:
        print("❌ No products found to save.")

if __name__ == "__main__":
    main()
