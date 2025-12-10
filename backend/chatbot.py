
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import mysql.connector # Driver per XAMPP
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# --- INCOLLA QUI LA TUA CHIAVE ---
API_KEY = "AIzaSyDKhBJMEBqVo34ieK-o4K7gEQQsCpiYcxs"
genai.configure(api_key=API_KEY)

istruzioni_poliba = """
Sei l'assistente virtuale ufficiale del sito del Politecnico di Bari (Poliba).
Rispondi in modo breve e professionale.
Se non sai una risposta, dì di visitare poliba.it.
"""

# =============================================================================
# 🐬 FUNZIONI DATABASE MYSQL (XAMPP)
# =============================================================================
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost", user="root", password="", database="poliba_chatbot"
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Errore connessione MySQL: {err}")
        return None

def get_percorso_from_mysql(chiave_cercata):
    conn = get_db_connection()
    percorso = None
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            query = "SELECT immagine_url, descrizione FROM mappe WHERE chiave = %s"
            cursor.execute(query, (chiave_cercata,))
            row = cursor.fetchone()
            if row:
                percorso = {"img": row["immagine_url"], "desc": row["descrizione"]}
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Errore Query: {e}")
    return percorso

# Memoria temporanea
contesto_utente = {"destinazione_pendente": None}

# =============================================================================
# RICERCA AUTOMATICA MODELLO
# =============================================================================
print("Sto cercando un modello funzionante...")
modello_scelto = None
chat_session = None

try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            if 'gemini-2.5-flash-lite' in m.name:
                modello_scelto = m.name
                break
            elif 'gemini-pro' in m.name:
                modello_scelto = m.name
            if not modello_scelto:
                modello_scelto = m.name

    if modello_scelto:
        print(f"TROVATO: {modello_scelto}")
        model = genai.GenerativeModel(modello_scelto)
        chat_session = model.start_chat(history=[])
    else:
        print("NESSUN MODELLO TROVATO.")
except Exception as e:
    print(f"Errore ricerca modelli: {e}")


@app.route('/chat', methods=['POST', 'OPTIONS'])
def chat_endpoint():
    if request.method == 'OPTIONS': return jsonify({"status": "ok"}), 200

    data = request.json
    messaggio_utente = data.get('message', '')
    if not messaggio_utente: return jsonify({"error": "Messaggio vuoto"}), 400

    print(f"Domanda: {messaggio_utente}")
    messaggio_lower = messaggio_utente.lower()

    # =============================================================================
    # LOGICA MAPPE SPECIALIZZATA
    # =============================================================================
    
    # A. IDENTIFICAZIONE LUOGO SPECIFICO
    # Cerchiamo solo i luoghi per cui hai le mappe
    if "dove" in messaggio_lower or "dov'è" in messaggio_lower or "posizione" in messaggio_lower or "come arrivo" in messaggio_lower:
        destinazione = None
        
        # 1. PoliLibrary
        if "biblioteca" in messaggio_lower or "library" in messaggio_lower:
            destinazione = "poliLibrary"
        
        # 2. Ufficio Mongiello
        elif "mongiello" in messaggio_lower:
            destinazione = "mongiello"
            
        # 3. Lab Elettronica / De Venuto
        elif "elettronica" in messaggio_lower or "de venuto" in messaggio_lower or "labddv" in messaggio_lower:
            destinazione = "LabDDV"
            
        if destinazione:
            contesto_utente["destinazione_pendente"] = destinazione
            
            # Mostriamo tutti gli ingressi possibili come opzioni
            return jsonify({
                "response": f"Per raggiungere {destinazione}, da quale ingresso accedi?",
                "type": "options", 
                "options": [
                    {"label": "📍 Via Orabona (Principale)", "value": "Orabona1"},
                    {"label": "📍 Via Orabona (Pedoni)", "value": "Orabona2"},
                    {"label": "📍 Via Re David", "value": "reDavid"},
                    {"label": "📍 Via Celso Ulpiani", "value": "ulpiani"}
                ]
            })

    # B. GESTIONE RISPOSTA E COSTRUZIONE CHIAVE DB
    ingressi_noti = ["Orabona1", "Orabona2", "reDavid", "ulpiani"]
    
    # Se il messaggio corrisponde a un valore dei bottoni (case sensitive nei valori, ma qui controlliamo lower)
    # Nota: Angular manda il 'value' del bottone, quindi ci aspettiamo es. "Orabona1"
    messaggio_input = messaggio_utente # Non usiamo lower per il match esatto del value se necessario, ma i valori sono camelCase
    
    # Troviamo se l'input corrisponde a uno degli ingressi noti (case insensitive per sicurezza)
    ingresso_trovato = next((i for i in ingressi_noti if i.lower() == messaggio_lower), None)

    if ingresso_trovato and contesto_utente["destinazione_pendente"]:
        dest = contesto_utente["destinazione_pendente"]
        start = ingresso_trovato
        chiave_db = ""

        # --- COSTRUZIONE CHIAVI SPECIFICHE (Mapping logico) ---
        
        # CASO 1: POLILIBRARY
        if dest == "poliLibrary":
            # Nel tuo DB hai: mappa_campus_poliLibrary_Orabona, _reDavid
            # Non distingui Orabona1/2 nel nome file per la library?
            # Assumo che entrambi gli Orabona portino alla chiave "Orabona" generica se non specificato diversamente
            if "Orabona" in start:
                chiave_db = "mappa_campus_poliLibrary_Orabona"
            elif start == "reDavid":
                chiave_db = "mappa_campus_poliLibrary_reDavid"
            else:
                chiave_db = "mappa_campus_poliLibrary" # Fallback generico

        # CASO 2: MONGIELLO
        elif dest == "mongiello":
            # Chiavi: ufficio_mongiello_Orabona1, _Orabona2, _reDavid
            chiave_db = f"ufficio_mongiello_{start}" 
            # Nota: se start è "ulpiani", non hai la mappa, darà errore (giustamente)

        # CASO 3: LAB ELETTRONICA (LabDDV)
        elif dest == "LabDDV":
            # Chiavi: immagine_campus_LabDDV_ulpiani, _reDavid, _Orabona1, _Orabona2
            chiave_db = f"immagine_campus_LabDDV_{start}"

        print(f"Cerco nel DB la chiave: {chiave_db}")
        
        percorso_data = get_percorso_from_mysql(chiave_db)
        contesto_utente["destinazione_pendente"] = None # Reset
        
        if percorso_data:
            return jsonify({
                "response": percorso_data["desc"],
                "type": "map",
                "mapUrl": percorso_data["img"],
                "mapTitle": f"Percorso per {dest}"
            })
        else:
            return jsonify({
                "response": f"Non ho una mappa specifica per questo percorso ({start} -> {dest}). Prova un altro ingresso.", 
                "type": "text"
            })

    # =============================================================================
    # LOGICA AI (FALLBACK)
    # =============================================================================
    if not modello_scelto: return jsonify({"error": "Errore AI"}), 500

    try:
        prompt = f"{istruzioni_poliba}\n\nUtente: {messaggio_utente}"
        response = chat_session.send_message(prompt)
        return jsonify({"response": response.text, "type": "text"})
    except Exception as e:
        if "429" in str(e):
            return jsonify({"response": "Troppe richieste. Riprova tra poco.", "type": "text"}), 200
        return jsonify({"response": "Errore AI.", "type": "text"}), 200

if __name__ == "__main__":
    app.run(debug=True, port=5000)