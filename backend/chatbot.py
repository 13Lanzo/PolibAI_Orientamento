
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import mysql.connector
import os
import traceback
from dotenv import load_dotenv
from kpi_data import get_kpi, get_all_course_ids, get_kpi_summary_for_prompt, find_course_id_by_name, COURSE_KPI

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
- INFOGRAFICHE: Se l'utente richiede un'infografica o se suggerisci un corso di ingegneria, informalo che può visualizzarle tramite i bottoni presenti sotto al tuo messaggio. NON GENERARE MAI nell'output LLM markdown di immagini e NON INCORPORARE MAI testi come "[Mostra Infografica]". L'interfaccia UI si occupa di far comparire i pulsanti automatici per te.

# [ANALISI QUANTITATIVA — DATI OPIS E ALMALAUREA]
Quando consigli o descrivi un corso di laurea, DEVI includere una sezione "📊 Dati alla mano" che citi cifre esatte estratte dai report ufficiali OPIS (Opinione Studenti) e AlmaLaurea (Condizione Occupazionale), se disponibili nei documenti forniti.
In particolare:
- OPIS: Cita punteggi su chiarezza espositiva dei docenti, stimolo dell'interesse, coerenza del carico di studio e reperibilità del docente.
- AlmaLaurea: Cita il tasso di occupazione a 1 anno dalla laurea, la retribuzione mensile netta media e la soddisfazione complessiva per il corso.
- GIUDIZIO COMPARATIVO: Se il tasso di occupazione è superiore alla media di Ateneo (68.5%), evidenzialo come punto di forza ("sopra la media di Ateneo"). Se inferiore, segnalalo come aspetto da considerare.
- Esempio di output atteso: "I dati AlmaLaurea 2024 mostrano un'ottima retribuzione media di 1.314€ netti. Dai rapporti OPIS, i docenti stimolano molto l'interesse (7.7/10), con un'ottima reperibilità (8.4/10)."

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
                if 'gemini-3.1-flash-lite' in m.name:
                    modello_scelto = m.name
                    break
                elif 'gemini-2.5-flash' in m.name:
                    modello_scelto = m.name
                elif 'gemini-1.5-flash' in m.name:
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
                    system_instruction=istruzioni_poliba,
                    tools=[{"google_search_retrieval": {}}]
                )
            except Exception as e:
                print("Supporto system_instruction/tools assente. Fallback standard.")
                model = genai.GenerativeModel(
                    model_name=modello_scelto,
                    tools=[{"google_search_retrieval": {}}]
                )
                initial_history.insert(0, {"role": "user", "parts": [istruzioni_poliba]})
                initial_history.insert(1, {"role": "model", "parts": ["Ricevuto. Seguirò queste istruzioni alla lettera."]})

            chat_session = model.start_chat(history=initial_history)
        else:
            print("NESSUN MODELLO TROVATO.")
except Exception as e:
    print(f"Errore ricerca modelli: {e}")

contesto_utente = {"destinazione_pendente": None}


@app.route('/chat', methods=['POST'])
def chat_endpoint():
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
    if messaggio_lower.strip() in ["mostra infografica", "infografica", "mostrami l'infografica", "voglio vedere l'infografica"]:
        return jsonify({
            "response": "Per poterti mostrare l'infografica esatta, ho bisogno di sapere a quale **Corso di Laurea** ti riferisci. Inserisci il nome del corso (es. 'Mostra infografica Ingegneria Gestionale').",
            "type": "text"
        })
    if not modello_scelto or not chat_session:
        return jsonify({"error": "Errore AI: Modello non disponibile"}), 500

    try:
        prompt = f"{istruzioni_poliba}\n\nUtente: {messaggio_utente}"
        response = chat_session.send_message(prompt)
        testo_risposta = response.text

        # =============================================================================
        # AGGIUNTA ID INFOGRAFICA ALLA RISPOSTA
        # =============================================================================
        testo_lower = testo_risposta.lower()
        
        mapping_keywords = [
            (["informatica", "automazione"], "IIA"),
            (["creatività digitale", "creativita digitale"], "ICD"),
            (["elettronica", "tecnologie internet"], "IETI"),
            (["civile", "ambientale e territoriale"], "ICIVAMB"),
            (["edile"], "IEDILE"),
            (["elettrica"], "IELE"),
            (["gestionale"], "IGEST"),
            (["meccanica"], "IMEC"),
            (["sistemi navali", "industriale"], "INAVAL"),
            (["medical", "sistemi medici", "lm-21", "lm21"], "IMED"),
            (["aerospazial", "sistemi aerospaziali"], "IAERO"),
            (["architettura", "lm-4", "lm4"], "ARCH"),
            (["design", "l4", "l-4"], "LDES"),
            (["costruzioni", "ambientale", "l-p01", "lp01", "laurea politecnica"], "LPOL")
        ]
        
        infografica_selezionata = None
        for kws, infografica_id in mapping_keywords:
            if any(kw in testo_lower for kw in kws):
                infografica_selezionata = infografica_id
                break

        print(f"Risposta AI inviata. Infografica ID: {infografica_selezionata}")
        risposta_json = {
            "response": testo_risposta,
            "type": "text",
            "options": []
        }
        if infografica_selezionata:
            risposta_json["infograficaId"] = infografica_selezionata
            
        return jsonify(risposta_json)
    except Exception as e:
        errore = str(e)
        print(f"Errore AI: {errore}")
        if "429" in errore:
            return jsonify({"response": "Troppe richieste. Riprova tra poco.", "type": "text"}), 200
        return jsonify({"response": "Errore AI generico.", "type": "text"}), 500


# =============================================================================
# ENDPOINT: ANALISI KPI CORSO (/analysis)
# =============================================================================

@app.route('/analysis', methods=['GET'])
def analysis_endpoint():
    """Restituisce i KPI strutturati per un dato course_id."""
    course_id = request.args.get('course_id', '').strip().upper()

    if not course_id:
        return jsonify({
            "error": "Parametro 'course_id' mancante.",
            "available_ids": get_all_course_ids()
        }), 400

    data = get_kpi(course_id)
    if not data:
        return jsonify({
            "error": f"Corso '{course_id}' non trovato nel database KPI.",
            "available_ids": get_all_course_ids()
        }), 404

    return jsonify(data)


# =============================================================================
# ENDPOINT: RACCOMANDAZIONE CORSO (Course Advisor AI)
# =============================================================================

istruzioni_advisor = """
Sei un orientatore universitario esperto del Politecnico di Bari (Poliba). Il tuo compito è analizzare gli interessi e le aspirazioni lavorative di uno studente e raccomandare il corso di laurea più adatto tra quelli offerti dal Poliba.

Ecco i corsi disponibili al Poliba (A.A. 2024-2025):
- Architettura (Magistrale a Ciclo Unico 5 anni, LM4, Dipartimento: ARCOD)
- Architecture Sciences for Heritage (Triennale, L17, Dipartimento: ARCOD, in inglese, NUOVO)
- Design (Triennale, L4, Dipartimento: ARCOD)
- Industrial Design (Magistrale, LM12, Dipartimento: ARCOD, in inglese)
- Costruzioni e Gestione Ambientale e Territoriale (Triennale Professionalizzante, L-P01, Dipartimento: DICATECh)
- Ingegneria Civile e Ambientale (Triennale, L7, Dipartimento: DICATECh)
- Ingegneria Edile (Triennale, L7, Dipartimento: DICATECh)
- Ingegneria della Mobilità Sostenibile (Magistrale, LM26, Dipartimento: DICATECh)
- Ingegneria Gestionale (Triennale, L9, Dipartimento: DMMM)
- Ingegneria Meccanica (Triennale, L9, Dipartimento: DMMM)
- Management Engineering for Innovation (Triennale, L9, Dipartimento: DMMM, in inglese, NUOVO)
- Ingegneria Industriale e dei Sistemi Navali (Triennale, L9, Dipartimento: DMMM)
- Ingegneria Elettrica (Triennale, L9, Dipartimento: DEI)
- Ingegneria dei Sistemi Aerospaziali (Triennale, L8, Dipartimento: DEI)
- Ingegneria dei Sistemi Medicali (Triennale, L8, Dipartimento: DEI)
- Energy Engineering (Magistrale, LM30, Dipartimento: DEI, in inglese)
- Automation and Robotics Engineering (Magistrale, LM32, Dipartimento: DIEI, in inglese)
- Computer Engineering (Magistrale, LM32, Dipartimento: DIEI, in inglese)
- Electronics Engineering (Magistrale, LM29, Dipartimento: DIEI, in inglese)
- Telecommunication and Internet Technologies Engineering (Magistrale, LM27, Dipartimento: DIEI, in inglese)
- Ingegneria Informatica e dell'Automazione (Triennale, L8, Dipartimento: DIEI)
- Ingegneria Elettronica e delle Tecnologie Internet (Triennale, L8, Dipartimento: DIEI)
- Ingegneria della Creatività Digitale (Triennale, L8, Dipartimento: DIEI, NUOVO)

INFORMAZIONI CHIAVE SUL POLIBA:
- 11.000 studenti, 93.8% occupati a 3 anni dalla laurea magistrale
- Sede principale a Bari, sedi a Taranto, Foggia, Brindisi
- Double Degree con NYU, Cranfield, NJ Tech, Illinois Tech, Grenoble, Côte d'Azur
- 6 corsi magistrali in inglese, Erasmus+ con 40+ università
- #9 top 10 italiano per Architettura & Design (QS Rankings 2024)
- Career Service con 500+ aziende partner, Career Fair annuale
- 5 dipartimenti: ARCOD (Architettura), DICATECh (Civile/Chimica), DMMM (Meccanica/Management), DEI (Elettrica/Aerospaziale), DIEI (Informatica/Elettronica)

Rispondi SEMPRE in italiano con questo formato JSON esatto (SOLO il JSON, nessun testo aggiuntivo, nessun blocco markdown):
{
  "corsoConsigliato": "Nome esatto del corso dalla lista sopra",
  "dipartimento": "Codice dipartimento (ARCOD, DICATECh, DMMM, DEI o DIEI)",
  "motivazione": "2-3 frasi che spiegano perché questo corso è perfetto per lo studente, usando un tono entusiasmante e personale",
  "puntiForza": ["punto 1", "punto 2", "punto 3"],
  "sbocchiLavorativi": ["sbocco 1", "sbocco 2", "sbocco 3"],
  "opportunitaInternazionali": "Descrizione breve delle opportunità internazionali specifiche per questo corso",
  "corsiAlternativi": ["Corso alternativo 1", "Corso alternativo 2"],
  "consiglio": "Un consiglio personale e motivazionale per lo studente (1-2 frasi)",
  "areeInteresse": [
    {"nome": "Area 1", "percentuale": 85},
    {"nome": "Area 2", "percentuale": 70},
    {"nome": "Area 3", "percentuale": 60},
    {"nome": "Area 4", "percentuale": 50},
    {"nome": "Area 5", "percentuale": 40},
    {"nome": "Area 6", "percentuale": 30}
  ]
}

REGOLE IMPORTANTI:
- areeInteresse deve contenere esattamente 6 aree rilevanti per il profilo dello studente con percentuali da 0 a 100
- Le percentuali indicano quanto ogni area è affine al profilo dello studente
- I nomi dei corsi devono corrispondere ESATTAMENTE alla lista
- Nella "motivazione", se hai dati OPIS/AlmaLaurea per il corso consigliato, CITA almeno 1-2 cifre chiave (es. tasso occupazione, retribuzione, punteggio chiarezza docenti)
- Rispondi SOLO con il JSON, nessun testo aggiuntivo, nessun blocco ```json
"""

@app.route('/recommend', methods=['POST'])
def recommend_endpoint():
    data = request.json
    materie = data.get('materie', [])
    aspirazioni = data.get('aspirazioni', [])
    note = data.get('note', '')

    if not materie and not aspirazioni:
        return jsonify({"error": "Inserisci almeno una materia o un'aspirazione"}), 400

    print(f"[ADVISOR] Materie: {materie}, Aspirazioni: {aspirazioni}, Note: {note}")

    if not modello_scelto:
        return jsonify({"error": "Modello AI non disponibile"}), 500

    user_message = f"""Materie preferite: {', '.join(materie) if materie else 'non specificate'}
Aspirazioni lavorative: {', '.join(aspirazioni) if aspirazioni else 'non specificate'}
Note aggiuntive: {note if note else 'nessuna'}

Analizza il mio profilo e consigliami il corso di laurea più adatto al Politecnico di Bari."""

    try:
        import json as json_module

        # Use a fresh model call (not the chat session) for advisor
        advisor_model = genai.GenerativeModel(model_name=modello_scelto)
        
        # Build parts with knowledge files if available
        parts = []
        if uploaded_files:
            parts.extend(uploaded_files)
        
        # Arricchisci il prompt con i dati KPI disponibili
        kpi_context = ""
        for cid in get_all_course_ids():
            summary = get_kpi_summary_for_prompt(cid)
            if summary:
                kpi_context += summary + "\n"
        
        if kpi_context:
            enriched_prompt = f"{istruzioni_advisor}\n\n--- DATI QUANTITATIVI DISPONIBILI ---\n{kpi_context}\n--- FINE DATI ---\n\n{user_message}"
        else:
            enriched_prompt = f"{istruzioni_advisor}\n\n{user_message}"
        
        parts.append(enriched_prompt)

        response = advisor_model.generate_content(parts)
        response_text = response.text.strip()
        
        # Clean up response - remove markdown code blocks if present
        if response_text.startswith("```"):
            response_text = response_text.split("\n", 1)[1] if "\n" in response_text else response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()

        parsed = json_module.loads(response_text)
        corso_consigliato = parsed.get('corsoConsigliato', '')
        print(f"[ADVISOR] Corso consigliato: {corso_consigliato}")
        
        # Cerca e allega i KPI del corso consigliato alla risposta
        course_id = find_course_id_by_name(corso_consigliato)
        if course_id:
            kpi = get_kpi(course_id)
            if kpi:
                parsed['kpiData'] = kpi
                parsed['courseKpiId'] = course_id
                print(f"[ADVISOR] KPI allegati per: {course_id}")
        
        return jsonify(parsed)

    except json_module.JSONDecodeError as je:
        print(f"[ADVISOR] Errore parsing JSON: {je}")
        print(f"[ADVISOR] Risposta raw: {response_text[:500]}")
        return jsonify({"error": "Errore nel formato della risposta AI"}), 500
    except Exception as e:
        errore = str(e)
        print(f"[ADVISOR] Errore: {errore}")
        if "429" in errore:
            return jsonify({"error": "Troppe richieste. Riprova tra poco."}), 429
        return jsonify({"error": "Errore nella raccomandazione AI"}), 500



if __name__ == "__main__":
    app.run(debug=True, port=5000)