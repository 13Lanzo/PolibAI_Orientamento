import os
from dotenv import load_dotenv
load_dotenv('backend/.env')
key = os.getenv('GOOGLE_API_KEY')
print(f"Key exists: {bool(key)}")
if key:
    from google import genai
    client = genai.Client(api_key=key)
    models = [m.name for m in client.models.list() if 'generateContent' in m.supported_actions]
    print(f"Modelli disponibili: {len(models)}")
    for m in models:
        if 'flash' in m.lower():
            print(f" - {m}")
