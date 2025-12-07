import logging
import json
import asyncio
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from sentence_transformers import SentenceTransformer
from tools import MockAmazonConnector, DatabaseManager
from price_tracker import PriceTracker

# Import Async Scrapers
from scrapers.amazon import AmazonScraper
from scrapers.flipkart import FlipkartScraper
from scrapers.ebay import EbayScraper

logger = logging.getLogger(__name__)

class ShoppingAgent:
    def __init__(self):
        self.connector = MockAmazonConnector()
        self.db_manager = DatabaseManager() 
        self.price_tracker = PriceTracker()
        
        logger.info("Agent: Initializing Models...")
        self.embed_model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
        self.llm = OllamaLLM(model="mistral",device='cuda')
        
        self.scrapers = {
            "Amazon": AmazonScraper(),
            "Flipkart": FlipkartScraper(),
            "eBay": EbayScraper(),
        }
        
    def get_user_profile_str(self):
        data = self.connector.get_user_data()
        if not data: return "User Profile: Guest"
        
        # Enhanced Profile String
        summary = f"User: {data.get('name', 'User')}\n"
        summary += f"- Budget: {data.get('budget_range', 'Unknown')}\n"
        summary += f"- Purpose: {data.get('purpose', 'General')}\n"
        
        if data.get('liked_brands'):
            summary += f"- Loves: {', '.join(data['liked_brands'])}\n"
        if data.get('disliked_brands'):
            summary += f"- Avoids: {', '.join(data['disliked_brands'])}\n"
            
        history = data.get('purchase_history', [])
        if history:
            summary += "- Recent Buys:\n"
            for item in history[-3:]: 
                summary += f"  * {item['product_name']} ({item['price']})\n"
                
        return summary

    async def search_online_async(self, query):
        """
        Async Cache-First Search.
        """
        # 1. Check Cache
        cached = self.db_manager.get_cached_results(query)
        if cached:
            logger.info("✅ Cache Hit!")
            return cached

        # 2. Parallel Async Scrape
        logger.info("⚡ parallel Scraping started...")
        tasks = []
        for name, scraper in self.scrapers.items():
            tasks.append(scraper.search(query))
            
        results_lists = await asyncio.gather(*tasks, return_exceptions=True)

        flat_results = []
        for res in results_lists:
            if isinstance(res, list):
                flat_results.extend(res)
        
        # Cold-start price advice: compute relative price ranking across all sources
        prices = [p.get('price', 0) for p in flat_results if isinstance(p.get('price', 0), (int, float)) and p.get('price', 0) > 0]
        prices_sorted = sorted(prices) if prices else []

        # Filter & Track Prices
        final_results = []
        for p in flat_results:
            if p['score'] > 0.2:
                # Compute cold-start trend if we have a comparable price set
                price = p.get('price', 0)
                trend = None
                if prices_sorted and isinstance(price, (int, float)) and price > 0:
                    # percentile rank
                    rank = sum(1 for x in prices_sorted if x <= price) / len(prices_sorted)
                    if rank <= 0.30:
                        trend = "✅ Good Deal vs peers (low percentile)"
                    elif rank >= 0.70:
                        trend = "⏳ High Price vs peers (consider waiting)"
                    else:
                        trend = "➡️ Fair Price vs peers"
                    p['trend'] = trend

                final_results.append(p)
                # Auto-track promising items
                if 'url' in p and p['url'] != "#":
                    self.price_tracker.track_item(
                        p.get('url'),
                        p.get('url'),
                        p.get('title'),
                        p.get('price', 0),
                        p.get('currency', 'USD'),
                        p.get('source', '')
                    )

        # 3. Store Cache
        if final_results:
            # Sort by price mostly
            final_results.sort(key=lambda x: x['price'] if x['price'] > 0 else 999999)
            self.db_manager.cache_results(query, final_results[:10]) # Store top 10
            
        return final_results[:5] # Return top 5

    def search_online_sync_wrapper(self, query):
        """Wrapper to call async search from synchronous context if needed."""
        # For Flask, we might run this. 
        # But ideally app.py handles event loop, or we just run loop here.
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop.run_until_complete(self.search_online_async(query))

    def chat(self, user_input, history_context=""):
        profile_context = self.get_user_profile_str()
        online_context = ""

        # Fast path for simple greetings / smalltalk: avoid heavy LLM + scraping
        msg = (user_input or "").strip().lower()
        simple_greetings = {"hi", "hello", "hey", "yo", "sup", "hii", "hiii"}
        shopping_keywords = ["buy", "find", "price", "deal", "cheap", "expensive", "recommend", "best"]
        if msg in simple_greetings or (len(msg.split()) <= 3 and not any(k in msg for k in shopping_keywords)):
            # Very short, friendly reply
            return "Hi! I am your shopping assistant. Tell me what you want to buy or your budget, and I will find options for you."
        # Retrieve recent interactions from Chroma (conversation memory)
        try:
            recent = self.db_manager.get_recent_interactions("current_user", limit=8)
            if recent:
                mem_lines = []
                for e in reversed(recent):  # oldest to newest for readability
                    role = e.get('role', 'user')
                    text = e.get('text', '')
                    mem_lines.append(f"{role}: {text}")
                history_context = (history_context + "\n" if history_context else "") + "\n".join(mem_lines)
        except Exception:
            pass
        
        # Decide Search (Simple Logic)
        if len(user_input.split()) > 1 or "buy" in user_input or "find" in user_input:
             products = self.search_online_sync_wrapper(user_input)
             
             if products:
                 online_context = "LIVE MARKET DATA:\n"
                 for p in products:
                     # Prefer cold-start trend if provided, else fall back to historical forecast
                     trend = p.get('trend') or self.price_tracker.get_forecast(p['url'])
                     online_context += f"- [{p['source']}] {p['title']} - {p['price']} {p['currency']}\n  ({trend}) [Link: {p['url']}]\n"
             else:
                 online_context = "No live results found.\n"

        template_str = """
        You are a Pro Agentic Shopping Assistant.
        Your style:
        - Be concise and practical.
        - For normal questions, give at most 3–4 key recommendations, each in 1–2 short sentences.
        - Do NOT write long essays.
        
        [USER PROFILE]
        {user_profile}
        
        [LIVE MARKET DATA & TRENDS]
        {market_data}
        
        [CONTEXT]
        {history}
        User query: {input}
        
        [GUIDANCE]
        1. Use 'LIVE MARKET DATA' to recommend.
        2. Mention Price Trends (e.g. "Price dropping, good time to buy!").
        3. Respect the user's Budget and Brands from [USER PROFILE].
        4. If they dislike a brand, DO NOT recommend it.
        5. Use very clear, short bullet points.
        
        Response:
        """
        
        prompt = ChatPromptTemplate.from_template(template_str)
        chain = prompt | self.llm
        
        try:
            response = chain.invoke({
                "user_profile": profile_context,
                "market_data": online_context,
                "history": history_context,
                "input": user_input
            })
            # Log interaction to conversation memory
            try:
                self.db_manager.log_interaction("current_user", "user", user_input)
                self.db_manager.log_interaction("current_user", "assistant", str(response))
            except Exception:
                pass
            return response
        except Exception as e:
            logger.error(f"Inference error: {e}")
            # Fallback: Compose a simple response without LLM
            summary_lines = [
                "[AUTO RESPONSE - LLM unavailable]",
                "Based on your profile and live market data:",
                "",
                "USER PROFILE:",
                profile_context,
                "",
                "MARKET DATA:",
                online_context or "No live results found.",
            ]
            fallback = "\n".join(summary_lines)
            try:
                self.db_manager.log_interaction("current_user", "user", user_input)
                self.db_manager.log_interaction("current_user", "assistant", fallback)
            except Exception:
                pass
            return fallback

    def train_preference(self, product_name, liked=True):
        # Update user profile dynamically
        if liked:
            self.connector.update_profile("liked_brands", [product_name]) # Simplified
        else:
             self.connector.update_profile("disliked_brands", [product_name])
        return True
