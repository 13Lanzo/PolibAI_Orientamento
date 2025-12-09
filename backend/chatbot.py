from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

#AIzaSyC1i84XdaciQCANtgZQdKw9Z2qNlQ7FerI    -> chiave di Lanzo

# --- INCOLLA QUI LA TUA CHIAVE ---
API_KEY = "AIzaSyDKhBJMEBqVo34ieK-o4K7gEQQsCpiYcxs"
genai.configure(api_key=API_KEY)

istruzioni_poliba = """
Sei l'assistente virtuale ufficiale del sito del Politecnico di Bari (Poliba).
Rispondi in modo breve e professionale.
Se non sai una risposta, dì di visitare poliba.it."""


# --- BLOCCO DI RICERCA AUTOMATICA DEL MODELLO ---
print("🔍 Sto cercando un modello funzionante per la tua Chiave API...")
modello_scelto = None

try:
    # Chiediamo a Google la lista dei modelli
    for m in genai.list_models():
        # Cerchiamo un modello che supporti la generazione di testo (generateContent)
        if 'generateContent' in m.supported_generation_methods:
            # Preferiamo gemini-pro se c'è, altrimenti va bene il primo che troviamo
            if 'gemini-2.5-flash-lite' in m.name:
                modello_scelto = m.name
                break
            elif 'gemini-pro' in m.name:
                modello_scelto = m.name
            
            # Se non abbiamo ancora scelto nulla, prendiamo questo come riserva
            if not modello_scelto:
                modello_scelto = m.name

    if modello_scelto:
        print(f"✅ TROVATO E SELEZIONATO: {modello_scelto}")
        model = genai.GenerativeModel(modello_scelto)
        chat_session = model.start_chat(history=[])
    else:
        print("❌ NESSUN MODELLO COMPATIBILE TROVATO. La chiave potrebbe non avere accessi.")

except Exception as e:
    print(f"❌ Errore nella ricerca modelli: {e}")


@app.route('/chat', methods=['POST', 'OPTIONS'])
def chat_endpoint():
    if request.method == 'OPTIONS':
        return jsonify({"status": "ok"}), 200

    if not modello_scelto:
        return jsonify({"error": "Errore interno: Nessun modello AI trovato."}), 500

    data = request.json
    messaggio_utente = data.get('message')
    print(f"📩 Domanda: {messaggio_utente}")

    if not messaggio_utente:
        return jsonify({"error": "Messaggio vuoto"}), 400

    try:
        # Costruiamo il prompt a mano per massima compatibilità
        prompt = f"{istruzioni_poliba}\n\nUtente: {messaggio_utente}"
        response = chat_session.send_message(prompt)
        print("📤 Risposta inviata!")
        return jsonify({"response": response.text})
    except Exception as e:
        print(f"🔥 Errore generazione: {e}")
        return jsonify({"response": "⚠️ Errore momentaneo del server AI."}), 200

if __name__ == "__main__":
    print("--- SERVER POLIBA AUTO-CONFIGURATO ---")
    app.run(debug=True, port=5000)


