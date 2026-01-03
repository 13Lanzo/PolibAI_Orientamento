import google.generativeai as genai
import os

# CHIAVE
API_KEY = ""
genai.configure(api_key=API_KEY)

print("Cerco i modelli disponibili per la tua chiave...")

try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"Trovato: {m.name}")
except Exception as e:
    print(f"Errore: {e}")
