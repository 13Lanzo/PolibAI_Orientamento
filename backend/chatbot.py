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


'''

from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import mysql.connector # Questa libreria serve per parlare con MySQL (XAMPP)
import os

# --- 1. CONFIGURAZIONE DEL SERVER WEB (FLASK) ---
app = Flask(__name__)
# CORS (Cross-Origin Resource Sharing) è fondamentale: permette al tuo sito Angular (che gira su una porta diversa)
# di inviare messaggi a questo server Python senza essere bloccato dal browser per sicurezza.
CORS(app, resources={r"/*": {"origins": "*"}})

# --- 2. CONFIGURAZIONE GOOGLE GEMINI (AI) ---
# Qui inserisci la tua chiave segreta. È come la password per usare il cervello di Google.
API_KEY = "AIzaSyDKhBJMEBqVo34ieK-o4K7gEQQsCpiYcxs"
genai.configure(api_key=API_KEY)

# Questo è il "System Prompt": istruzioni che diamo all'AI prima ancora che l'utente parli.
istruzioni_poliba = """
Sei l'assistente virtuale ufficiale del sito del Politecnico di Bari (Poliba).
Rispondi in modo breve e professionale.
Se non sai una risposta, dì di visitare poliba.it.
"""

# =============================================================================
# 🐬 NUOVO: FUNZIONI DATABASE MYSQL (XAMPP)
# =============================================================================

def get_db_connection():
    """
    Questa funzione serve ad aprire il 'tubo' di collegamento con XAMPP.
    Se XAMPP è spento, questa funzione fallirà e restituirà None.
    """
    try:
        conn = mysql.connector.connect(
            host="localhost",       # Il database è sul tuo computer locale
            user="root",            # Utente standard di XAMPP
            password="",            # Di default XAMPP non ha password
            database="poliba_chatbot" # Il nome del DB che abbiamo creato con lo script di setup
        )
        return conn
    except mysql.connector.Error as err:
        print(f"❌ Errore connessione MySQL: {err}")
        return None

def get_percorso_from_mysql(chiave_cercata):
    """
    Questa funzione cerca una specifica mappa nel database.
    Input: chiave_cercata (es. 'ingresso_aulamagna')
    Output: Un dizionario con l'url dell'immagine e la descrizione, oppure None se non trova nulla.
    """
    conn = get_db_connection() # Apriamo la connessione
    percorso = None
    
    if conn:
        try:
            # Il cursore è come un 'dito' che scorre le righe della tabella.
            # dictionary=True ci permette di leggere i dati per nome (row['descrizione']) invece che per numero.
            cursor = conn.cursor(dictionary=True)
            
            # Prepariamo la query SQL. Usiamo %s al posto della variabile per sicurezza (evita SQL Injection).
            query = "SELECT immagine_url, descrizione FROM mappe WHERE chiave = %s"
            cursor.execute(query, (chiave_cercata,))
            
            # Prendiamo il primo risultato trovato
            row = cursor.fetchone()
            
            if row:
                # Se abbiamo trovato qualcosa, lo impacchettiamo in un oggetto pulito
                percorso = {"img": row["immagine_url"], "desc": row["descrizione"]}
            
            # Chiudiamo tutto per liberare memoria
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"❌ Errore Query: {e}")
            
    return percorso

# Variabile globale per la "memoria a breve termine".
# Serve quando l'utente chiede "Dov'è l'aula magna?" -> Il bot deve ricordarsi che l'utente vuole l'aula magna
# mentre gli chiede "Dove ti trovi ora?".
contesto_utente = {"destinazione_pendente": None}


# =============================================================================
# 🔍 TUA LOGICA DI RICERCA AUTOMATICA DEL MODELLO
# =============================================================================
# Questo blocco serve a trovare quale "versione" di Gemini è disponibile per la tua chiave.
# È utile perché a volte Google cambia i nomi o i permessi dei modelli gratuiti.

print("🔍 Sto cercando un modello funzionante per la tua Chiave API...")
modello_scelto = None
chat_session = None

try:
    # Chiediamo a Google la lista di tutti i modelli disponibili
    for m in genai.list_models():
        # Controlliamo se il modello sa generare testo ('generateContent')
        if 'generateContent' in m.supported_generation_methods:
            
            # Priorità 1: Cerchiamo 'gemini-2.5-flash-lite' (nuovo e veloce)
            if 'gemini-2.5-flash-lite' in m.name:
                modello_scelto = m.name
                break # Trovato il migliore! Smettiamo di cercare.
            
            # Priorità 2: Cerchiamo 'gemini-pro' (più potente ma a volte lento)
            elif 'gemini-pro' in m.name:
                modello_scelto = m.name
            
            # Priorità 3: Se non abbiamo ancora nulla, prendiamo il primo che capita
            if not modello_scelto:
                modello_scelto = m.name

    if modello_scelto:
        print(f"✅ TROVATO E SELEZIONATO: {modello_scelto}")
        # Inizializziamo il modello scelto
        model = genai.GenerativeModel(modello_scelto)
        # Avviamo una sessione di chat vuota
        chat_session = model.start_chat(history=[])
    else:
        print("❌ NESSUN MODELLO COMPATIBILE TROVATO. La chiave potrebbe non avere accessi.")

except Exception as e:
    print(f"❌ Errore nella ricerca modelli: {e}")


# =============================================================================
# 🌐 ENDPOINT DELLA CHAT (Qui arrivano i messaggi da Angular)
# =============================================================================
@app.route('/chat', methods=['POST', 'OPTIONS'])
def chat_endpoint():
    # Se il browser chiede "posso parlarti?" (OPTIONS), rispondiamo sì.
    if request.method == 'OPTIONS':
        return jsonify({"status": "ok"}), 200

    # Leggiamo il messaggio inviato dall'utente (JSON)
    data = request.json
    messaggio_utente = data.get('message', '')
    
    # Controllo di sicurezza: se il messaggio è vuoto, diamo errore
    if not messaggio_utente:
        return jsonify({"error": "Messaggio vuoto"}), 400

    print(f"📩 Domanda: {messaggio_utente}")
    messaggio_lower = messaggio_utente.lower() # Convertiamo tutto in minuscolo per facilitare i controlli

    # =============================================================================
    # 📍 FASE 1: LOGICA MAPPE (Interviene PRIMA dell'AI)
    # =============================================================================
    
    # CASO A: L'utente chiede DOVE si trova qualcosa ("Dov'è l'aula magna?")
    # Controlliamo se ci sono parole chiave come "dove", "posizione" e il nome di un luogo.
    if "dove" in messaggio_lower or "dov'è" in messaggio_lower or "posizione" in messaggio_lower:
        destinazione = None
        
        # Cerchiamo di capire quale luogo vuole l'utente
        if "aula magna" in messaggio_lower: destinazione = "aulamagna"
        elif "lab" in messaggio_lower: destinazione = "labinfo"
        elif "segreteria" in messaggio_lower: destinazione = "segreteria"
            
        if destinazione:
            # 1. Salviamo nella "memoria" che l'utente vuole andare lì
            contesto_utente["destinazione_pendente"] = destinazione
            
            # 2. Rispondiamo chiedendo il punto di partenza (con i BOTTONI)
            # type: 'options' dice al Frontend di mostrare i pulsanti invece del testo normale
            return jsonify({
                "response": f"Certo! Per indicarti la strada corretta per {destinazione}, dimmi dove ti trovi adesso:",
                "type": "options",  
                "options": [
                    {"label": "📍 Ingresso", "value": "ingresso"},
                    {"label": "☕ Bar", "value": "bar"},
                    {"label": "📄 Segreteria", "value": "segreteria"}
                ]
            })

    # CASO B: L'utente ha cliccato un bottone (es. "ingresso")
    # Verifichiamo se il messaggio corrisponde a un luogo di partenza E se stavamo aspettando una risposta.
    luoghi_partenza = ["ingresso", "bar", "segreteria"]
    if any(l in messaggio_lower for l in luoghi_partenza) and contesto_utente["destinazione_pendente"]:
        
        # Capiamo da dove parte (es. "ingresso")
        start_point = next((l for l in luoghi_partenza if l in messaggio_lower), "ingresso")
        # Recuperiamo dove voleva andare dalla memoria
        destinazione = contesto_utente["destinazione_pendente"]
        
        # Creiamo la chiave univoca per il DB (es. "ingresso_aulamagna")
        chiave_db = f"{start_point}_{destinazione}"
        
        # >>> CHIAMATA AL DATABASE MYSQL <<<
        # Chiediamo al DB: "Dammi l'immagine per il percorso ingresso->aulamagna"
        percorso_data = get_percorso_from_mysql(chiave_db)
        
        # Resettiamo la memoria (abbiamo finito questa interazione)
        contesto_utente["destinazione_pendente"] = None 
        
        if percorso_data:
            # Se il DB ha risposto, mandiamo la MAPPA al frontend
            return jsonify({
                "response": percorso_data["desc"],
                "type": "map", # Dice al frontend di mostrare il widget immagine
                "mapUrl": percorso_data["img"],
                "mapTitle": f"Da {start_point.capitalize()} a {destinazione.capitalize()}"
            })
        else:
            # Se il percorso non esiste nel DB, diamo un errore gentile
            return jsonify({"response": "⚠️ Mappa non trovata nel database.", "type": "text"})

    # =============================================================================
    # 🤖 FASE 2: LOGICA AI (Fallback per tutto il resto)
    # Se non era una richiesta di mappa, lasciamo rispondere Gemini.
    # =============================================================================
    
    if not modello_scelto:
        return jsonify({"error": "Errore interno: Nessun modello AI trovato."}), 500

    try:
        # Costruiamo il prompt unendo le istruzioni segrete ("Sei il bot del Poliba") alla domanda dell'utente.
        prompt = f"{istruzioni_poliba}\n\nUtente: {messaggio_utente}"
        
        # Inviamo la richiesta a Google
        response = chat_session.send_message(prompt)
        print("📤 Risposta inviata!")
        
        # Restituiamo la risposta testuale generata dall'AI
        return jsonify({"response": response.text, "type": "text"})
    
    except Exception as e:
        print(f"🔥 Errore generazione: {e}")
        return jsonify({"response": "⚠️ Errore momentaneo del server AI.", "type": "text"}), 200

if __name__ == "__main__":
    print("--- SERVER POLIBA AUTO-CONFIGURATO + MAPPE MYSQL ---")
    app.run(debug=True, port=5000)

'''
