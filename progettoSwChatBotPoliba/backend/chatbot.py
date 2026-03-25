
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
API_KEY = os.getenv("GOOGLE_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)
else:
    print("ERRORE: Chiave API mancante nel file .env")

istruzioni_poliba = """
# [RUOLO E IDENTITÀ]
Sei "Poliba Orientamento AI PRO", l'Assistente Virtuale Ufficiale e Raccomandatore dell'Offerta Formativa del Politecnico di Bari (POLIBA). 
Sei un'Intelligenza Artificiale di nuova generazione: esperta, accogliente, empatica e dotata di capacità avanzate (visione, ricerca in tempo reale, generazione di immagini). 

# [OBIETTIVO PRINCIPALE]
Il tuo scopo è guidare futuri studenti, iscritti, docenti e visitatori. Devi fornire informazioni precisissime su didattica (inclusa la Guida agli Studi 2024/2025 e i nuovi corsi come Ingegneria della Creatività Digitale), servizi, logistica, eventi, tasse ed Erasmus, aiutando gli utenti a prendere decisioni consapevoli sul loro futuro accademico.

# [REGOLE FONDAMENTALI E LIMITI DI DOMINIO]
1. DOMINIO STRETTO: Rispondi ESCLUSIVAMENTE a domande relative al mondo universitario e al Politecnico di Bari. Se l'utente devia su argomenti esterni, declina con cortesia ed empatia, riportando la conversazione sull'orientamento universitario.
2. FONTI E DOCUMENTI (RAG): Basa SEMPRE le tue risposte sui documenti ufficiali forniti nel contesto (Guida dello Studente, Regolamenti, Bandi). Estrai con precisione regole, requisiti, CFU ed esami.
3. ZERO ALLUCINAZIONI E RICERCA WEB: Non inventare MAI scadenze, date o requisiti. Se un'informazione (es. scadenze TOLC-I, avvisi recenti) non è nei tuoi documenti, utilizza l'integrazione Google Search per cercare aggiornamenti in tempo reale sul sito ufficiale "poliba.it". Se ancora non trovi la risposta, invita l'utente a contattare la Segreteria Studenti.

# [UTILIZZO DELLE FUNZIONALITÀ AVANZATE MULTIMODALI]
- ANALISI PAGELLE/DIPLOMI (Vision): Se l'utente carica l'immagine di una pagella o un documento, analizza i voti, individua le materie in cui eccelle (es. Matematica, Fisica, Disegno) e le sue attitudini. Basandoti su questo, suggerisci 2-3 corsi di laurea del Poliba altamente compatibili, motivando la tua scelta in modo incoraggiante.
- LETTURA GRAFICI: Se l'utente carica brochure o grafici del Poliba, estrai i dati salienti e spiegali in linguaggio semplice e accessibile.
- INFOGRAFICHE: Se l'utente richiede un'infografica o se suggerisci un corso di ingegneria, informalo che può cliccare sul bottone "Mostra Infografica" sottostante per visualizzarla. Nelle opzioni rapide verrà inserito il bottone per mostrare l'infografica pertinente.

# [GUIDA E NAVIGAZIONE DEL CAMPUS]
Agisci come una guida esperta del Campus del Politecnico di Bari.
- Quando riconosci intenti legati alla navigazione ("dov'è...", "come raggiungo..."), identifica chiaramente la destinazione.
- Fornisci indicazioni descrittive, logiche e passo-passo (es. "Entrando dall'ingresso principale di Via Orabona...").
- Specifica SEMPRE l'Edificio (es. "Edificio Q01"), il Dipartimento e, se noto, il Piano o i punti di riferimento vicini (es. Bar, Biblioteca).

# [STILE DI COMUNICAZIONE E FORMATTAZIONE]
- Tono: Cordiale, istituzionale ma giovanile, ispiratore e amichevole. Dai sempre del "tu" allo studente.
- Formattazione (Markdown): 
  * Usa il **grassetto** per evidenziare parole chiave, nomi dei corsi, scadenze e luoghi.
  * Usa elenchi puntati o numerati per spezzare procedure, requisiti o elenchi di materie.
  * Mantieni i paragrafi brevi e ariosi per facilitare la lettura, specialmente per chi usa l'interfaccia vocale.
  * Inserisci emoji coerenti (es. 🎓, 📍, 💡, 📅) per rendere l'interfaccia visivamente più accattivante, senza esagerare.
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
# CARICAMENTO PDF CONOSCENZA AUTENTICA E INIZIALIZZAZIONE MODELLO
# =============================================================================
print("Inizializzazione Gemini e caricamento conoscenza...")
uploaded_files = []
try:
    if API_KEY:
        knowledge_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "knowledge")
        if os.path.exists(knowledge_dir):
            for filename in os.listdir(knowledge_dir):
                if filename.lower().endswith(".pdf"):
                    pdf_path = os.path.join(knowledge_dir, filename)
                    print(f"Caricamento {filename}...")
                    file_ref = genai.upload_file(pdf_path)
                    uploaded_files.append(file_ref)
                    print(f"-> Caricato come URI: {file_ref.uri}")
except Exception as e:
    print(f"Errore caricamento PDF: {e}")

modello_scelto = None
chat_session = None

try:
    if API_KEY:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                if 'gemini-3-flash-preview' in m.name:
                    modello_scelto = m.name
                    break
                elif 'gemini-2.5-flash' in m.name or 'gemini-1.5-flash' in m.name:
                    modello_scelto = m.name
                
                if not modello_scelto:
                    modello_scelto = m.name

        if modello_scelto:
            print(f"TROVATO: {modello_scelto}")
            
            initial_history = []
            if uploaded_files:
                parts = uploaded_files + ["Questi sono i documenti ufficiali del Politecnico di Bari. Usali come base di conoscenza primaria per rispondere a tutte le domande."]
                initial_history.append({"role": "user", "parts": parts})
                initial_history.append({"role": "model", "parts": ["Certamente! Ho assimilato i documenti ufficiali e li utilizzerò come fonte principale per assistere l'utente in modo preciso."]})
            
            try:
                model = genai.GenerativeModel(
                    model_name=modello_scelto,
                    system_instruction=istruzioni_poliba
                )
            except Exception as e:
                print("Supporto system_instruction assente. Fallback standard.")
                model = genai.GenerativeModel(model_name=modello_scelto)
                initial_history.insert(0, {"role": "user", "parts": [istruzioni_poliba]})
                initial_history.insert(1, {"role": "model", "parts": ["Ricevuto. Seguirò queste istruzioni alla lettera."]})

            chat_session = model.start_chat(history=initial_history)
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
    # LOGICA INFOGRAFICHE STATICHE LATO BACKEND
    # =============================================================================
    if messaggio_utente.startswith("INFO_"):
        codice_corso = messaggio_utente.replace("INFO_", "")
        mappa_img = {
            "L7_IngegneriaEdile": "ingegneria_edile.jpg", # Placeholder matching the name asked by the user or actual
            "L8_IngegneriaSistemiMedicali": "ingegneria_sistemi_medicali.jpg",
            "L8_IngegneriaCreativitaDigitale": "ingegneria_creativita_digitale.jpg",
            "L9_IngegneriaMeccanica": "L9-IngegneriaMeccanica.png",
            "L8_IngegneriaInformaticaAutomazione": "ingegneria_informatica_automazione.jpg"
        }
        
        if codice_corso in mappa_img:
            # Pulizia per il testo a schermo (aggiungendo spazi prima delle maiuscole)
            import re
            nome_pulito = codice_corso.split("_", 1)[1] if "_" in codice_corso else codice_corso
            nome_spaziato = re.sub(r'([A-Z])', r' \1', nome_pulito).strip()
            
            return jsonify({
                "response": f"Ecco l'infografica per il corso di laurea in **{nome_spaziato}**.",
                "type": "image",
                "mapUrl": f"assets/infografiche/{mappa_img[codice_corso]}"
            })

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
        testo_risposta = response.text

        # =============================================================================
        # AGGIUNTA DINAMICA OPZIONI ("Bottone Infografica")
        # =============================================================================
        testo_lower = testo_risposta.lower()
        opzioni_infografica = []
        
        if ("l7" in testo_lower or "l-7" in testo_lower) and "edile" in testo_lower:
            opzioni_infografica.append({"label": "🖼️ Mostra Infografica Ingegneria Edile", "value": "INFO_L7_IngegneriaEdile"})
            
        if ("l8" in testo_lower or "l-8" in testo_lower) and ("medical" in testo_lower or "sistemi medicali" in testo_lower or "sistemi medici" in testo_lower):
            opzioni_infografica.append({"label": "🖼️ Mostra Infografica Sistemi Medicali", "value": "INFO_L8_IngegneriaSistemiMedicali"})
            
        if ("l8" in testo_lower or "l-8" in testo_lower) and ("creatività digitale" in testo_lower or "creativita digitale" in testo_lower):
            opzioni_infografica.append({"label": "🖼️ Mostra Infografica Creatività Digitale", "value": "INFO_L8_IngegneriaCreativitaDigitale"})
            
        if ("l9" in testo_lower or "l-9" in testo_lower) and "meccanica" in testo_lower:
            opzioni_infografica.append({"label": "🖼️ Mostra Infografica Ingegneria Meccanica", "value": "INFO_L9_IngegneriaMeccanica"})
            
        if ("l8" in testo_lower or "l-8" in testo_lower) and ("informatica" in testo_lower or "automazione" in testo_lower):
            # Preveniamo attivazioni doppie con creatività digitale
            if not any(opt['value'] == "INFO_L8_IngegneriaCreativitaDigitale" for opt in opzioni_infografica):
                opzioni_infografica.append({"label": "🖼️ Mostra Infografica Ing. Informatica e Automazione", "value": "INFO_L8_IngegneriaInformaticaAutomazione"})

        print("Risposta AI inviata con opzioni aggiuntive calcolate!")
        if opzioni_infografica:
            return jsonify({"response": testo_risposta, "type": "text", "options": opzioni_infografica})
        else:
            return jsonify({"response": testo_risposta, "type": "text"})
    except Exception as e:
        errore = str(e)
        print(f"Errore AI: {errore}")
        if "429" in errore:
            return jsonify({"response": "Troppe richieste. Riprova tra poco.", "type": "text"}), 200
        return jsonify({"response": "Errore AI generico.", "type": "text"}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)