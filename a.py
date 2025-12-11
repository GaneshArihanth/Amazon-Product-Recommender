import google.generativeai as genai

genai.configure(api_key="AIzaSyC_UxXozPLKiz2GiEbL7hBPRc67EGjJTkw")

models = genai.list_models()

for m in models:
    print("MODEL:", m.name)
    print("Supported:", m.supported_generation_methods)
    print()
