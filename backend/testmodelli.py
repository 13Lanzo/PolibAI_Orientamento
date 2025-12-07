import google.generativeai as genai
import os

# INSERISCI LA TUA CHIAVE
API_KEY = "AIzaSyDKhBJMEBqVo34ieK-o4K7gEQQsCpiYcxs"
genai.configure(api_key=API_KEY)

print("🔍 Cerco i modelli disponibili per la tua chiave...")

try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"✅ Trovato: {m.name}")
except Exception as e:
    print(f"❌ Errore: {e}")
