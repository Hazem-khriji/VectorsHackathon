from fastapi import FastAPI, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from src.app.services.search import search_service
from src.app.services.user import user_service

app = FastAPI(title="FinCommerce API", version="0.1.0")

class Product(BaseModel):
    id: str | int
    title: str
    price: float
    description: str
    category: str
    rating: float
    image: str
    source: str = "unknown"
    score: Optional[float] = None
    emi_available: bool = False
    merchant: str = "Unknown"

class SearchResponse(BaseModel):
    results: List[Product]
    user_context: Optional[dict] = None

@app.get("/")
def read_root():
    return {"message": "Welcome to FinCommerce API"}

@app.get("/search", response_model=SearchResponse)
def search_products(
    q: str = Query(..., description="Search query"),
    user_id: Optional[int] = Query(None, description="User ID for context")
):
    # 1. Get User Context (if provided)
    user_context = None
    if user_id:
        user = user_service.get_user_by_id(user_id)
        if user:
            user_context = {
                "username": user.username,
                "balance": user.balance,
                "budget": user.monthly_budget
            }
    
    # 2. Perform Search
    raw_results = search_service.search_products(q, limit=10)
    
    # 3. Format Results (and future enrichment)
    formatted_results = []
    for item in raw_results:
        # Basic mapping - ensure default values if keys missing
        product = Product(
            id=item.get('id', 0),
            title=item.get('title', 'Unknown'),
            price=item.get('price', 0.0),
            description=item.get('description', ''),
            category=item.get('category', 'general'),
            rating=item.get('rating', 0.0),
            image=item.get('image', ''),
            source=item.get('source', 'unknown'),
            score=item.get('score'),
            emi_available=item.get('emi_available', False),
            merchant=item.get('merchant', 'Unknown')
        )
        formatted_results.append(product)

    return SearchResponse(results=formatted_results, user_context=user_context)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
