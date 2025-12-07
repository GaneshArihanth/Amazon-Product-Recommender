import os
import json
import logging
import chromadb
from chromadb.config import Settings
import datetime
import uuid

logger = logging.getLogger(__name__)

class MockAmazonConnector:
    """
    Enhanced User Profile Connector.
    """
    def __init__(self, data_file_path=None):
        if data_file_path is None:
            data_file_path = os.path.join(os.getcwd(), 'data', 'mock_data.json')
        self.data_file_path = data_file_path
        self.current_user_id = "current_user"
        self._ensure_schema()

    def _ensure_schema(self):
        """Ensures the mock data has new profile fields."""
        if not os.path.exists(self.data_file_path): return
        
        with open(self.data_file_path, 'r') as f:
            data = json.load(f)
        
        user = data['users'].get(self.current_user_id, {})
        updates = False
        
        defaults = {
            "budget_range": "Medium ($50 - $200)",
            "purpose": "General Use",
            "liked_brands": [],
            "disliked_brands": [],
            "browsing_history": []
        }
        
        for k, v in defaults.items():
            if k not in user:
                user[k] = v
                updates = True
                
        if updates:
            data['users'][self.current_user_id] = user
            with open(self.data_file_path, 'w') as f:
                json.dump(data, f, indent=2)

    def get_user_data(self):
        try:
            with open(self.data_file_path, 'r') as f:
                data = json.load(f)
                return data['users'].get(self.current_user_id, {})
        except Exception as e:
            logger.error(f"Error reading mock data: {e}")
            return {}

    def update_profile(self, key, value):
        try:
            with open(self.data_file_path, 'r') as f:
                data = json.load(f)
            
            user = data['users'].get(self.current_user_id)
            if user:
                user[key] = value
                with open(self.data_file_path, 'w') as f:
                    json.dump(data, f, indent=2)
            return True
        except Exception as e:
            return False

    def simulate_purchase(self, product_name, category, price=0.0):
        try:
            with open(self.data_file_path, 'r') as f:
                data = json.load(f)
            
            user = data['users'].get(self.current_user_id)
            if not user: return False

            new_purchase = {
                "product_name": product_name,
                "category": category,
                "price": price,
                "purchase_date": datetime.date.today().isoformat()
            }
            user['purchase_history'].append(new_purchase)
            
            with open(self.data_file_path, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error stimulating purchase: {e}")
            return False

class DatabaseManager:
    """
    Manages interactions with ChromaDB (Caching Logic).
    """
    def __init__(self, persist_path=None):
        if persist_path is None:
            persist_path = os.path.join(os.getcwd(), 'chroma_db')
        
        self.client = chromadb.PersistentClient(path=persist_path)
        self.user_history_collection_name = "user_interaction_history"
        self.product_cache_collection_name = "product_cache"

    def get_or_create_collection(self, name):
        try:
            return self.client.get_collection(name)
        except:
            return self.client.create_collection(name)

    def get_cached_results(self, query):
        try:
            collection = self.get_or_create_collection(self.product_cache_collection_name)
            query_id = query.lower().replace(" ", "_")
            results = collection.get(ids=[query_id])
            if results['documents']:
                return json.loads(results['documents'][0])
            return None
        except Exception as e:
            logger.error(f"Cache retrieval error: {e}")
            return None

    def cache_results(self, query, products):
        try:
            collection = self.get_or_create_collection(self.product_cache_collection_name)
            query_id = query.lower().replace(" ", "_")
            timestamp = datetime.datetime.now().isoformat()
            doc_content = json.dumps(products)
            collection.upsert(
                ids=[query_id],
                documents=[doc_content],
                metadatas=[{"timestamp": timestamp, "query": query}]
            )
            logger.info(f"Cached {len(products)} items for '{query}'")
        except Exception as e:
            logger.error(f"Cache storage error: {e}")

    # --- Conversation Memory (User Interaction History) ---
    def log_interaction(self, user_id: str, role: str, text: str, ts: str | None = None):
        try:
            collection = self.get_or_create_collection(self.user_history_collection_name)
            event_id = f"{user_id}:{uuid.uuid4().hex}"
            if ts is None:
                ts = datetime.datetime.utcnow().isoformat()
            document = json.dumps({
                "user_id": user_id,
                "role": role,
                "text": text,
                "ts": ts,
            })
            collection.add(
                ids=[event_id],
                documents=[document],
                metadatas=[{"user_id": user_id, "role": role, "ts": ts}]
            )
        except Exception as e:
            logger.error(f"Interaction log error: {e}")

    def get_recent_interactions(self, user_id: str, limit: int = 10):
        try:
            collection = self.get_or_create_collection(self.user_history_collection_name)
            data = collection.get(where={"user_id": user_id})
            docs = data.get("documents", []) or []
            entries = []
            for d in docs:
                try:
                    entries.append(json.loads(d))
                except Exception:
                    continue
            # Sort by timestamp descending and return the last N
            entries.sort(key=lambda x: x.get("ts", ""), reverse=True)
            return entries[:limit]
        except Exception as e:
            logger.error(f"Interaction retrieval error: {e}")
            return []
