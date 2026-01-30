import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import uvicorn
import logging
from datetime import datetime
from App.RAG_pipeline import Pipeline
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional
import shutil
from pathlib import Path

# Setup logging for observability
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('search_logs.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

UPLOAD_DIR = Path("uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)



ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
]


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import index creation functions (from root directory)
try:
    from create_indexes import create_product_index
    from create_behavior_indexes import create_behavioral_index
except ImportError:
    # Fallback if imports fail (e.g. if path issues)
    logger.error("Could not import index creation scripts")
    create_product_index = None
    create_behavioral_index = None

@app.on_event("startup")
async def startup_event():
    """
    Run startup tasks:
    1. Create/Verify Qdrant Indexes
    """
    logger.info("Running startup tasks...")
    try:
        if create_product_index:
            logger.info("Initializing product indexes...")
            create_product_index()
        
        if create_behavioral_index:
            logger.info("Initializing behavioral indexes...")
            create_behavioral_index()
            
    except Exception as e:
        logger.error(f"Startup task failed: {e}")

# create a pipeline class
pipeline_rag = Pipeline()


@app.post("/api/search")
async def search_products(
        query: Optional[str] = Form(None),
        image: Optional[UploadFile] = File(None)
):
    """
    Endpoint to handle text query and/or image upload
    """
    try:
        image_path = None
        if image:
            image_path = UPLOAD_DIR/image.filename
            with image_path.open("wb") as buffer:
                shutil.copyfileobj(image.file, buffer)

        if not query and not image:
            raise HTTPException(status_code=400, detail="Please provide a query or image")

        search_query = query if query else ""

        result = pipeline_rag.pipeline(
            query=search_query,
            image_path=str(image_path) if image_path else None
        )

        if image_path and image_path.exists():
            image_path.unlink()

        return JSONResponse(content={
            "success": True,
            "data": result
        })
    except Exception as e:
        if image_path and image_path.exists():
            image_path.unlink()

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e)
            }
        )

@app.get("/")
async def root():
    return {"message": "Product Search API is running"}


# Behavior tracking endpoint for user actions
from App.user_behavior import UserBehaviorTracker

# Initialize the tracker
user_tracker = UserBehaviorTracker()

@app.post("/api/track")
async def track_event(request: Request):
    """
    Track user behavior events and store as vectors in Qdrant for personalization
    """
    try:
        data = await request.json()
        session_id = data.get('session_id', 'anonymous')
        event_type = data.get('event_type', 'unknown')
        timestamp = data.get('timestamp', datetime.now().isoformat())
        
        # Log the event for observability
        logger.info(f"TRACK_EVENT | session={session_id} | type={event_type} | data={data} | time={timestamp}")
        
        # Store in Qdrant
        user_tracker.track_event(session_id, event_type, data)
        
        return JSONResponse(content={
            "success": True,
            "message": "Event tracked and stored successfully"
        })
    except Exception as e:
        logger.error(f"TRACK_ERROR | error={str(e)}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

@app.get("/api/recommendations")
async def get_recommendations(session_id: str):
    """
    Get personalized recommendations based on user's session history
    """
    try:
        # Get cumulative user context (e.g. "laptop t-shirt shoes")
        user_context_query = user_tracker.get_cumulative_context(session_id, limit=20)
        
        if not user_context_query:
            # Fallback for new users: Return "Trending" products
            # In a real app, this would be computed from global popularity
            results = hybrid_searcher.search("best selling electronics fashion", limit=12)
            reason = "Trending Products"
        else:
            # Use the cumulative context to find products matching ANY of the user's interests
            # The hybrid searcher's embedding model will find vectors close to this 'mixed' profile
            results = hybrid_searcher.search(user_context_query, limit=12)
            reason = "Based on your activity history"
            
        # Format results
        products = []
        for i, product in enumerate(results):
            products.append({
                "id": i,
                "category": product.get("category", "Unknown"),
                "rating": product.get("rating", 0),
                "actual_price": product.get("actual_price", 0),
                "discounted_price": product.get("discounted_price", 0),
                "image_url": product.get("image_url", "").strip('"'),
                "product_url": product.get("product_url", "")
            })
            
        return JSONResponse(content={
            "success": True,
            "data": products[:4], # Return top 4 personalized picks
            "reason": reason
        })
    except Exception as e:
        logger.error(f"RECOMMENDATION_ERROR | error={str(e)}")
        return JSONResponse(content={"success": False, "error": str(e)})


# New endpoint for test2 frontend - returns structured product data
from App.Hybrid_Search import HybridSearcher

hybrid_searcher = HybridSearcher("products")

@app.post("/api/search-products")
async def search_products_structured(
        query: Optional[str] = Form(None),
        max_budget: Optional[float] = Form(None),
        monthly_allowance: Optional[float] = Form(None),
        image: Optional[UploadFile] = File(None)
):
    """
    Endpoint to search products and return both AI explanation and structured product data
    Supports financial context (budget filtering) and Image Search
    """
    try:
        # Handle image upload and description
        image_description = ""
        image_path = None
        
        if image:
            image_path = UPLOAD_DIR/image.filename
            with image_path.open("wb") as buffer:
                shutil.copyfileobj(image.file, buffer)
            
            # Get description from LLM
            try:
                # Need to pass 'self' implicitly by calling the method on the instance
                print(f"DEBUG: describing image {image_path}")
                image_description = pipeline_rag.describe_image(str(image_path))
                print(f"DEBUG: image description result: {image_description}")
            except Exception as e:
                print(f"DEBUG: Image description failed: {e}")
                logger.error(f"IMAGE_DESC_ERROR | error={str(e)}")
        
        # Combine user query with image description
        base_query = query.strip() if query else ""
        search_query = f"{base_query} {image_description}".strip()

        if not search_query:
             # Cleanup if no query at all
            if image_path and image_path.exists():
                image_path.unlink()
            raise HTTPException(status_code=400, detail="Please provide a search query or an image")
        
        # Log the search for observability
        logger.info(f"SEARCH_REQUEST | query='{search_query}' | budget={max_budget} | monthly={monthly_allowance}")
        
        # Get AI explanation from RAG pipeline
        ai_response = pipeline_rag.pipeline(
            query=search_query,
            image_path=None # We already extracted the description
        )

        # Clean up image after processing
        if image_path and image_path.exists():
            image_path.unlink()

        # Get products from Qdrant using hybrid search for product cards
        results = hybrid_searcher.search(search_query)

        # Format and categorize results (Soft Filtering)
        products = []
        for i, product in enumerate(results):
            price = product.get("discounted_price", 0)
            formatted_product = {
                "id": i,
                "category": product.get("category", "Unknown"),
                "rating": product.get("rating", 0),
                "actual_price": product.get("actual_price", 0),
                "discounted_price": price,
                "image_url": product.get("image_url", "").strip('"'),
                "product_url": product.get("product_url", ""),
                "match_type": "match",
                "message": ""
            }

            # 1. Budget Filter
            if max_budget:
                if price <= max_budget:
                     products.append(formatted_product)
                
                # 2. Monthly Installment Filter (Alternative)
                elif monthly_allowance and (price / 12) <= monthly_allowance:
                    formatted_product["match_type"] = "alternative_installment"
                    formatted_product["message"] = f"Fits monthly budget (${price/12:.0f}/mo)"
                    products.append(formatted_product)
                
                # 3. Close Alternative (+25% over budget)
                elif price <= (max_budget * 1.25):
                    formatted_product["match_type"] = "alternative_close"
                    formatted_product["message"] = f"Only ${price - max_budget:.0f} over budget"
                    products.append(formatted_product)
                
                # Else: Hidden (Too expensive)
            else:
                # No budget set -> All are matches
                products.append(formatted_product)

        # Log results
        logger.info(f"SEARCH_RESULTS | query='{search_query}' | count={len(products)}")

        return JSONResponse(content={
            "success": True,
            "ai_response": ai_response,
            "data": products,
            "count": len(products)
        })
    except Exception as e:
        logger.error(f"SEARCH_ERROR | query='{query}' | error={str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e)
            }
        )


@app.get("/api/products")
async def get_all_products(page: int = 1, limit: int = 12, session_id: Optional[str] = None):
    """
    Endpoint to fetch products.
    If session_id provided & history exists -> returns MIXED PERSONALIZED FEED.
    Else -> returns generic feed (Scroll).
    """
    try:
        # Get total count (approximation for search, exact for scroll)
        collection_info = hybrid_searcher.qdrant_client.get_collection("products")
        total_count = collection_info.points_count
        
        # Calculate offset
        offset = (page - 1) * limit

        # Check for personalization context
        top_interests = []
        if session_id:
            # Get top 3 categories of interest
            top_interests = user_tracker.get_personalized_recommendations(session_id, limit=3)
            # top_interests is list of (category, score) tuples
            print(f"DEBUG: Top interests for session {session_id}: {top_interests}")

        products = []
        
        if top_interests:
            # MIXED PERSONALIZED FEED
            logger.info(f"FETCH_FEED | mode=mixed_personalized | session={session_id} | interests={top_interests}")
            
            # Strategy: Fetch results for each top category separately and mix them
            # We split the limit among the categories (e.g., if limit=12 and 2 categories, fetch 6 of each)
            num_categories = len(top_interests)
            per_category_limit = max(4, limit // num_categories) # Ensure at least a few per category
            
            category_results = []
            for category, score in top_interests:
                # Search for products in this category (boosted by 'best rated')
                # We add 'best' to ensure high quality items from that category show up
                query = f"best {category}" 
                results = hybrid_searcher.search(query, limit=per_category_limit)
                category_results.append(results)
            
            # Interleave results: [Cat1-Item1, Cat2-Item1, Cat3-Item1, Cat1-Item2, ...]
            # Using zip_longest would be ideal, but simple round-robin is fine
            from itertools import zip_longest
            
            # Flatten the interleaved list
            mixed_results = []
            for items in zip_longest(*category_results):
                for item in items:
                    if item:
                        # Deduplicate based on payload/id if needed, but for now just add
                        # Check strictly for duplicates to avoid showing same item twice
                        if item not in mixed_results:
                            mixed_results.append(item)
            
            # Apply offset and limit to the mixed result set
            # Note: This 'page' logic is imperfect for mixed feeds without a dedicated search engine feature
            # but works for a hackathon demo. Effectively checks "fresh" mixed results each time.
            # To make pagination work "better" with this naive mix, we might just slice the front
            # or regenerate new random ones. For now, we return the first N mixed.
            results_to_show = mixed_results[:limit]

            for i, product in enumerate(results_to_show):
                products.append({
                    "id": offset + i, # Virtual ID
                    "category": product.get("category", "Unknown"),
                    "rating": product.get("rating", 0),
                    "actual_price": product.get("actual_price", 0),
                    "discounted_price": product.get("discounted_price", 0),
                    "image_url": product.get("image_url", "").strip('"'),
                    "product_url": product.get("product_url", "")
                })
                
        else:
            # GENERIC FEED (Fall back to DB scroll)
            logger.info(f"FETCH_FEED | mode=generic | session={session_id}")
            results, next_offset = hybrid_searcher.qdrant_client.scroll(
                collection_name="products",
                limit=limit,
                offset=offset,
                with_payload=True,
            )
            
            for i, point in enumerate(results):
                product = point.payload
                products.append({
                    "id": offset + i,
                    "category": product.get("category", "Unknown"),
                    "rating": product.get("rating", 0),
                    "actual_price": product.get("actual_price", 0),
                    "discounted_price": product.get("discounted_price", 0),
                    "image_url": product.get("image_url", "").strip('"'),
                    "product_url": product.get("product_url", "")
                })

        # Calculate total pages
        total_pages = (total_count + limit - 1) // limit

        return JSONResponse(content={
            "success": True,
            "data": products,
            "count": len(products),
            "total_count": total_count,
            "total_pages": total_pages,
            "current_page": page,
            "has_next": page < total_pages,
            "has_prev": page > 1
        })
    except Exception as e:
        logger.error(f"FEED_ERROR | mode=mixed | error={str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e)
            }
        )


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
