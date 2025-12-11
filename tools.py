import os
import json
import logging
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
    Manages local JSON-backed caches and interaction history.
    """
    def __init__(self, persist_path=None):
        base_path = os.getenv("STORAGE_PATH") or persist_path or os.path.join(os.getcwd(), 'chroma_db')
        os.makedirs(base_path, exist_ok=True)
        self.base_path = base_path
        self.cache_file = os.path.join(self.base_path, 'product_cache.json')
        self.history_file = os.path.join(self.base_path, 'user_history.json')
        if not os.path.exists(self.cache_file):
            with open(self.cache_file, 'w') as f:
                json.dump({}, f)
        if not os.path.exists(self.history_file):
            with open(self.history_file, 'w') as f:
                json.dump([], f)

    def _read_cache(self):
        try:
            with open(self.cache_file, 'r') as f:
                return json.load(f)
        except Exception:
            return {}

    def _write_cache(self, data):
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Cache write error: {e}")

    def _read_history(self):
        try:
            with open(self.history_file, 'r') as f:
                return json.load(f)
        except Exception:
            return []

    def _write_history(self, data):
        try:
            with open(self.history_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"History write error: {e}")

    def get_cached_results(self, query):
        try:
            all_cache = self._read_cache()
            query_id = query.lower().replace(" ", "_")
            entry = all_cache.get(query_id)
            if entry and isinstance(entry.get('documents'), list):
                return entry['documents']
            return None
        except Exception as e:
            logger.error(f"Cache retrieval error: {e}")
            return None

    def cache_results(self, query, products):
        try:
            all_cache = self._read_cache()
            query_id = query.lower().replace(" ", "_")
            timestamp = datetime.datetime.now().isoformat()
            all_cache[query_id] = {
                "documents": products,
                "metadata": {"timestamp": timestamp, "query": query}
            }
            self._write_cache(all_cache)
            logger.info(f"Cached {len(products)} items for '{query}'")
        except Exception as e:
            logger.error(f"Cache storage error: {e}")

    def log_interaction(self, user_id: str, role: str, text: str, ts: str | None = None):
        try:
            history = self._read_history()
            if ts is None:
                ts = datetime.datetime.utcnow().isoformat()
            history.append({
                "id": f"{user_id}:{uuid.uuid4().hex}",
                "user_id": user_id,
                "role": role,
                "text": text,
                "ts": ts,
            })
            self._write_history(history)
        except Exception as e:
            logger.error(f"Interaction log error: {e}")

    def get_recent_interactions(self, user_id: str, limit: int = 10):
        try:
            history = self._read_history()
            entries = [h for h in history if h.get("user_id") == user_id]
            entries.sort(key=lambda x: x.get("ts", ""), reverse=True)
            return entries[:limit]
        except Exception as e:
            logger.error(f"Interaction retrieval error: {e}")
            return []
