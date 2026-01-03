
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import mysql.connector
import os
import traceback
from dotenv import load_dotenv

# Carica variabili d'ambiente
load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# --- CONFIGURAZIONE CHIAVE API ---
# Leggiamo dal file .env per sicurezza
API_KEY = os.getenv("GOOGLE_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)
else:
    print("ERRORE: Chiave API mancante nel file .env")

istruzioni_poliba = """
SEI L'ASSISTENTE VIRTUALE UFFICIALE DEL POLITECNICO DI BARI (POLIBA).
Il tuo obiettivo è assistere studenti, docenti e visitatori con informazioni precise, tono accademico ma accessibile.

### REGOLE FONDAMENTALI:
1.  *Dominio Stretto:* Rispondi SOLO a domande relative al Politecnico di Bari (didattica, servizi, logistica, eventi). Se l'argomento è esterno, declina gentilmente.
2.  *No Allucinazioni:* Se non conosci un'informazione specifica, suggerisci di visitare il sito ufficiale poliba.it.
3.  *Formattazione:* Usa elenchi puntati per le procedure e grassetto per i concetti chiave.

### GESTIONE INTELLIGENTE LUOGHI E NAVIGAZIONE:
Devi agire come una guida esperta del Campus. Riconosci automaticamente richieste riguardanti mappe, aule, uffici e luoghi di interesse, anche quando formulate con linguaggio naturale (es. "dov'è...", "come raggiungo...", "posizione di...").

*Compiti specifici per la navigazione:*
1.  *Analisi dell'Input:* Identifica chiaramente l'intento dell'utente. Se chiede indicazioni, cerca di capire:
    * *Destinazione:* Dove vuole andare l'utente?
    * *Punto di Partenza:* Deduci dove si trova l'utente. Se l'utente dice "non so arrivare all'aula magna", assumi che abbia bisogno di un orientamento generale. Se dice "mi trovo all'ingresso", calcola il percorso da lì. Se il punto di partenza non è chiaro, chiedilo gentilmente ("Da dove stai partendo?").
2.  *Risposta di Orientamento:* Fornisci indicazioni descrittive chiare basate sulla struttura del Campus (es. "Entrando da Via Orabona, prosegui dritto per il viale principale, l'edificio si trova sulla destra...").
3.  *Riferimenti Edifici:* Quando citi un luogo, specifica sempre l'Edificio (es. "Edificio Q01") e il Piano se noti, per facilitare l'orientamento.
"""

# =============================================================================
# DATABASE MYSQL (XAMPP)
# =============================================================================
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost", user="root", password="", database="poliba_chatbot"
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Errore MySQL: {err}")
        return None

def get_percorso_from_mysql(chiave_cercata):
    conn = get_db_connection()
    percorso = None
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT immagine_url, descrizione FROM mappe WHERE chiave = %s", (chiave_cercata,))
            row = cursor.fetchone()
            if row:
                percorso = {"img": row["immagine_url"], "desc": row["descrizione"]}
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Errore Query: {e}")
    return percorso

# =============================================================================
# RICERCA AUTOMATICA MODELLO 
# =============================================================================
print("Ricerca modello funzionante...")
modello_scelto = None
chat_session = None

try:
    if API_KEY:
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

contesto_utente = {"destinazione_pendente": None}


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
    
    # A. IDENTIFICAZIONE LUOGO
    if "dove" in messaggio_lower or "dov'è" in messaggio_lower or "posizione" in messaggio_lower or "come arrivo" in messaggio_lower:
        destinazione = None
        
        if "biblioteca" in messaggio_lower or "library" in messaggio_lower:
            destinazione = "poliLibrary"
        elif "mongiello" in messaggio_lower:
            destinazione = "mongiello"
        elif "elettronica" in messaggio_lower or "de venuto" in messaggio_lower or "labddv" in messaggio_lower:
            destinazione = "LabDDV"
            
        if destinazione:
            global contesto_utente
            contesto_utente = destinazione
            
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

    # B. GESTIONE RISPOSTA BOTTONI
    ingressi_noti = ["Orabona1", "Orabona2", "reDavid", "ulpiani"]
    
    # Cerca se nel messaggio c'è un valore noto (es. value del bottone)
    # Nota: Angular manda il 'value' (es. Orabona1), quindi cerchiamo quello
    ingresso_trovato = next((i for i in ingressi_noti if i.lower() in messaggio_lower), None)

    # Verifica se 'contesto_utente' è una stringa (la destinazione)
    destinazione_salvata = contesto_utente if isinstance(contesto_utente, str) else None

    if ingresso_trovato and destinazione_salvata:
        start = ingresso_trovato
        dest = destinazione_salvata
        chiave_db = ""

        # --- COSTRUZIONE CHIAVI ---
        if dest == "poliLibrary":
            if "Orabona" in start: chiave_db = "mappa_campus_poliLibrary_Orabona"
            elif "reDavid" in start: chiave_db = "mappa_campus_poliLibrary_reDavid"
            else: chiave_db = "mappa_campus_poliLibrary" # Fallback

        elif dest == "mongiello":
            chiave_db = f"ufficio_mongiello_{start}"

        elif dest == "LabDDV":
            chiave_db = f"immagine_campus_LabDDV_{start}"

        print(f"Cerco chiave: {chiave_db}")
        
        percorso_data = get_percorso_from_mysql(chiave_db)
        
        # Reset contesto (usando global per modificarla correttamente)
        contesto_utente = None 
        
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
    # LOGICA AI 
    # =============================================================================
    if not modello_scelto or not chat_session:
        return jsonify({"error": "Errore AI: Modello non disponibile"}), 500

    try:
        prompt = f"{istruzioni_poliba}\n\nUtente: {messaggio_utente}"
        response = chat_session.send_message(prompt)
        print("Risposta AI inviata!")
        return jsonify({"response": response.text, "type": "text"})
    except Exception as e:
        errore = str(e)
        print(f"Errore AI: {errore}")
        if "429" in errore:
            return jsonify({"response": "Troppe richieste. Riprova tra poco.", "type": "text"}), 200
        return jsonify({"response": "Errore AI generico.", "type": "text"}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)