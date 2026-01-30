"""
User Behavior Tracker with Qdrant Storage

This module stores user interactions as vectors in Qdrant for personalization.
It creates user preference vectors based on:
- Search queries
- Product clicks  
- Add to cart actions

These vectors can be used to re-rank search results and provide personalized recommendations.
"""

from qdrant_client import QdrantClient, models
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from datetime import datetime
import hashlib
import logging

logger = logging.getLogger(__name__)


class UserBehaviorTracker:
    """
    Tracks user behavior and stores it in Qdrant for personalization.
    
    Creates embeddings from user actions to build preference profiles.
    """
    
    COLLECTION_NAME = "user_behaviors"
    DENSE_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    
    def __init__(self, qdrant_url: str = None):
        import os
        if qdrant_url is None:
            qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
        self.qdrant_client = QdrantClient(
            url=qdrant_url,
            api_key=os.getenv("QDRANT_API_KEY")
        )
        self._ensure_collection_exists()
    
    def _ensure_collection_exists(self):
        """Create the user_behaviors collection if it doesn't exist."""
        try:
            collections = self.qdrant_client.get_collections().collections
            collection_names = [c.name for c in collections]
            
            if self.COLLECTION_NAME not in collection_names:
                self.qdrant_client.create_collection(
                    collection_name=self.COLLECTION_NAME,
                    vectors_config={
                        "behavior": VectorParams(
                            size=384,  # all-MiniLM-L6-v2 output size
                            distance=Distance.COSINE
                        )
                    }
                )
                logger.info(f"Created collection: {self.COLLECTION_NAME}")
        except Exception as e:
            logger.error(f"Error creating collection: {e}")
    
    def _generate_point_id(self, session_id: str, timestamp: str) -> str:
        """Generate a unique point ID from session and timestamp."""
        hash_input = f"{session_id}_{timestamp}"
        return int(hashlib.md5(hash_input.encode()).hexdigest()[:16], 16)
    
    def _create_behavior_text(self, event_type: str, data: dict) -> str:
        """
        Create a text representation of the behavior for embedding.
        This text captures the user's intent.
        """
        if event_type == "search":
            query = data.get("query", "")
            budget = data.get("budget", "")
            if budget:
                return f"User searched for: {query} with budget ${budget}"
            return f"User searched for: {query}"
        
        elif event_type == "product_click":
            category = data.get("category", "product")
            price = data.get("price", "")
            return f"User clicked on {category} priced at ${price}"
        
        elif event_type == "add_to_cart":
            category = data.get("category", "product")
            price = data.get("price", "")
            return f"User added {category} to cart, price ${price}"
        
        else:
            return f"User action: {event_type}"
    
    def track_event(self, session_id: str, event_type: str, data: dict) -> bool:
        """
        Store a user behavior event in Qdrant with vector embedding.
        
        Args:
            session_id: Unique user session identifier
            event_type: Type of event (search, product_click, add_to_cart)
            data: Event data (query, category, price, etc.)
        
        Returns:
            True if successful, False otherwise
        """
        try:
            timestamp = datetime.now().isoformat()
            behavior_text = self._create_behavior_text(event_type, data)
            
            # Create the point with behavior embedding
            point_id = self._generate_point_id(session_id, timestamp)
            
            # Use Qdrant's built-in embedding
            self.qdrant_client.upsert(
                collection_name=self.COLLECTION_NAME,
                points=[
                    models.PointStruct(
                        id=point_id,
                        vector={
                            "behavior": models.Document(
                                text=behavior_text,
                                model=self.DENSE_MODEL
                            )
                        },
                        payload={
                            "session_id": session_id,
                            "event_type": event_type,
                            "data": data,
                            "behavior_text": behavior_text,
                            "timestamp": timestamp,
                            # Weight for importance: cart > click > search
                            "weight": self._get_event_weight(event_type)
                        }
                    )
                ]
            )
            
            logger.info(f"STORED_BEHAVIOR | session={session_id} | type={event_type} | text='{behavior_text}'")
            return True
            
        except Exception as e:
            logger.error(f"BEHAVIOR_STORE_ERROR | error={str(e)}")
            return False
    
    def _get_event_weight(self, event_type: str) -> float:
        """
        Assign weights to different event types.
        Higher weight = stronger preference signal.
        """
        weights = {
            "add_to_cart": 1.0,  # Strongest signal
            "product_click": 0.5,  # Medium signal
            "search": 0.3,  # Weaker signal
        }
        return weights.get(event_type, 0.2)
    
    def get_user_preferences(self, session_id: str, limit: int = 10) -> list:
        """
        Get recent behavior history for a user session.
        
        Returns list of behavior records sorted by recency.
        """
        try:
            results = self.qdrant_client.scroll(
                collection_name=self.COLLECTION_NAME,
                scroll_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="session_id",
                            match=models.MatchValue(value=session_id)
                        )
                    ]
                ),
                limit=limit,
                with_payload=True,
                with_vectors=False
            )
            
            points = results[0]
            behaviors = [point.payload for point in points]
            # Sort by timestamp (newest first)
            behaviors.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            return behaviors
            
        except Exception as e:
            logger.error(f"GET_PREFERENCES_ERROR | error={str(e)}")
            return []
    
    def get_personalized_recommendations(self, session_id: str, limit: int = 5) -> list:
        """
        Get product categories the user has shown interest in.
        
        Returns weighted list of preferred categories/products.
        """
        behaviors = self.get_user_preferences(session_id, limit=50)
        
        # Aggregate preferences by category/interest with weights
        interest_scores = {}
        for behavior in behaviors:
            event_type = behavior.get("event_type", "")
            data = behavior.get("data", {})
            weight = behavior.get("weight", 0.2)
            
            # Use category if available, otherwise use search query
            interest = data.get("category", "")
            if not interest and event_type == "search":
                interest = data.get("query", "")
            
            if interest:
                # Normalize interest text
                interest = interest.strip().lower()
                interest_scores[interest] = interest_scores.get(interest, 0) + weight
        
        # Sort by score and return top interests
        sorted_interests = sorted(
            interest_scores.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        return sorted_interests[:limit]

    def get_cumulative_context(self, session_id: str, limit: int = 15) -> str:
        """
        Aggregate recent user behaviors into a single context string.
        Used to create a 'Cumulative User Vector' for search.
        Results in a string like "laptop t-shirt smartwatch"
        """
        # Get more history to ensure we capture diverse interests
        behaviors = self.get_user_preferences(session_id, limit=limit)
        
        context_parts = []
        seen_items = set()
        
        for behavior in behaviors:
            event_type = behavior.get("event_type")
            data = behavior.get("data", {})
            
            # Extract meaningful content
            content = ""
            if event_type == "search":
                content = data.get("query", "")
            elif event_type in ["product_click", "add_to_cart"]:
                # Use category as the primary signal
                content = data.get("category", "")
                
            content = content.strip().lower()
            
            # Add to context if valid and not a duplicate (to prevent "laptop laptop laptop")
            if content and content not in seen_items:
                context_parts.append(content)
                seen_items.add(content)
        
        # specific fallback if no valid behavior found
        if not context_parts:
            return ""
            
        return " ".join(context_parts)
