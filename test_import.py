import traceback
try:
    print("Importing SentenceTransformer...")
    from sentence_transformers import SentenceTransformer
    print("Model init...")
    model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
    print("Success")
except Exception:
    traceback.print_exc()
