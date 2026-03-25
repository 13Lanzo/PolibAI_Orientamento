import requests
import json
import time

url = "http://127.0.0.1:5000/chat"
headers = {"Content-Type": "application/json"}
payload = {"message": "Genera un'infografica per Ingegneria Meccanica"}

print(f"Inviando richiesta a {url}...")
try:
    response = requests.post(url, headers=headers, json=payload)
    print("Status:", response.status_code)
    data = response.json()
    print("Type:", data.get("type"))
    print("Testo:", data.get("response"))
    if "mapUrl" in data:
        print("Image base64 caricata, len:", len(data["mapUrl"]))
except Exception as e:
    print("Errore richiesta:", e)
