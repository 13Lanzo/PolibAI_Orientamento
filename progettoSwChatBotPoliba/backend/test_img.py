import google.generativeai as genai
import os
import base64
from dotenv import load_dotenv

load_dotenv("c:/Users/Lanzo/OneDrive/Desktop/progetto_sw/progettoSwChatBotPoliba/backend/.env")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

try:
    print("Test generazione immagine...")
    image_model = genai.GenerativeModel('models/gemini-2.5-flash-image')
    response = image_model.generate_content("Una mela rossa")
    
    found = False
    for candidate in response.candidates:
        for part in candidate.content.parts:
            if hasattr(part, 'inline_data') and part.inline_data:
                b64_data = base64.b64encode(part.inline_data.data).decode('utf-8')
                mime_type = part.inline_data.mime_type
                print(f"Successo! Mime: {mime_type}, len={len(b64_data)}")
                found = True
                break
    
    if not found:
        print("Non ha restituito inline_data. Response:", response.text)

except Exception as e:
    print(f"Errore: {e}")
