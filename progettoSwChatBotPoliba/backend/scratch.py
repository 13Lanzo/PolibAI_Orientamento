import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

try:
    print("Modelli per generazione immagini:")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods or 'generateImage' in m.supported_generation_methods or 'predict' in m.supported_generation_methods:
            if 'image' in m.name.lower() or 'vision' in m.name.lower() or 'imagen' in m.name.lower():
                print(f"Name: {m.name}, Methods: {m.supported_generation_methods}")
except Exception as e:
    print(f"Error: {e}")
