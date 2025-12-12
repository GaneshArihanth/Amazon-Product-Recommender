import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

def list_models():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("❌ Error: GEMINI_API_KEY is missing from your .env file.")
        return

    print(f"Checking models for API Key ending in: ...{api_key[-5:]}")
    
    try:
        client = genai.Client(api_key=api_key)
        
        print("\n--- AVAILABLE MODELS ---")
        count = 0
        
        # In the new SDK, we just list models. 
        # Most "gemini" models support content generation.
        for model in client.models.list():
            display_name = getattr(model, "display_name", "Unknown")
            name = model.name
            
            # Simple filter: only show "gemini" models
            if "gemini" in name:
                print(f"✅ {name} ({display_name})")
                count += 1
        
        if count == 0:
            print("\n❌ No 'gemini' models found. Check if your API Key is from AI Studio.")
        else:
            print(f"\nTotal models found: {count}")
            print("Use one of the names above (e.g., 'gemini-1.5-flash') in your a.py file.")

    except Exception as e:
        print(f"\n❌ Error connecting to Google: {e}")

if __name__ == "__main__":
    list_models()