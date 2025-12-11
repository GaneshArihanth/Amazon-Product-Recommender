import traceback
try:
    print("Importing google.generativeai...")
    import google.generativeai as genai
    print("Success: google-generativeai available")
except Exception:
    traceback.print_exc()
