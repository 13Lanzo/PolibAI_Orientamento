
from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai
# pyrefly: ignore [missing-import]
from google.genai import types
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
    client = genai.Client(api_key=API_KEY)
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
Quando consigli o descrivi un corso di laurea, DEVI includere una sezione "📊 Dati alla mano" solo se nel contesto sono presenti KPI strutturati o documenti Markdown verificabili (report OPIS e AlmaLaurea).
In particolare:
- OPIS: I dati sono espressi come "% Giudizi Negativi" per varie aree (chiarezza docenti, stimolo interesse, carico studio, reperibilità). Una percentuale bassa di giudizi negativi indica un buon risultato.
- AlmaLaurea: Cita il tasso di occupazione a 1 anno dalla laurea, la retribuzione mensile netta media, la soddisfazione complessiva e i dati di progressione a 5 anni se disponibili.
- GIUDIZIO COMPARATIVO: Confronta i dati del corso con la media di Ateneo solo quando la media è presente nei KPI o nei documenti forniti.
- Non usare esempi numerici come fonte: ogni cifra deve provenire dal contesto KPI o dalla knowledge base Markdown.

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
# CARICAMENTO KNOWLEDGE BASE (PDF + MD) E INIZIALIZZAZIONE MODELLO
# =============================================================================
print("Inizializzazione Gemini e caricamento conoscenza...")
uploaded_files = []
markdown_context_parts = []
try:
    if API_KEY:
        # Recupera file già caricati su Gemini per evitare caricamenti duplicati e velocizzare l'avvio
        print("Recupero lista file già caricati su Gemini...")
        existing_files = {}
        try:
            for f in client.files.list():
                existing_files[f.display_name] = f
            print(f"Trovati {len(existing_files)} file già caricati su Gemini File API.")
        except Exception as list_err:
            print(f"Errore nel recupero della lista file da Gemini API: {list_err}")
            existing_files = {}

        knowledge_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "knowledge")
        if os.path.exists(knowledge_dir):
            for root, dirs, files in os.walk(knowledge_dir):
                for filename in sorted(files):
                    filepath = os.path.join(root, filename)
                    rel_path = os.path.relpath(filepath, knowledge_dir)
                    import urllib.parse
                    safe_name = urllib.parse.quote(filename)

                    if filename.lower().endswith(".pdf"):
                        if safe_name in existing_files:
                            print(f"PDF già presente su Gemini: {rel_path} (riutilizzo)...")
                            uploaded_files.append(existing_files[safe_name])
                        else:
                            print(f"Caricamento PDF: {rel_path}...")
                            try:
                                file_ref = client.files.upload(file=filepath, config={'display_name': safe_name})
                                uploaded_files.append(file_ref)
                                print(f"-> Caricato come URI: {file_ref.uri}")
                            except Exception as upload_err:
                                print(f"-> Upload PDF fallito ({upload_err}). Il file non sarà disponibile nella knowledge base.")
                    elif filename.lower().endswith((".md", ".json")):
                        ext = "MD" if filename.lower().endswith(".md") else "JSON"
                        mime = "text/plain" if filename.lower().endswith(".md") else "application/json"
                        
                        if safe_name in existing_files:
                            print(f"File {ext} già presente su Gemini: {rel_path} (riutilizzo)...")
                            uploaded_files.append(existing_files[safe_name])
                        else:
                            print(f"Caricamento {ext}: {rel_path}...")
                            try:
                                file_ref = client.files.upload(file=filepath, config={'mime_type': mime, 'display_name': safe_name})
                                uploaded_files.append(file_ref)
                                print(f"-> Caricato come file API: {file_ref.uri}")
                            except Exception as upload_err:
                                print(f"-> Upload file fallito ({upload_err}), caricamento come testo...")
                                with open(filepath, "r", encoding="utf-8") as f:
                                    content = f.read()
                                markdown_context_parts.append(f"--- DOCUMENTO {ext}: {rel_path} ---\n{content}\n--- FINE DOCUMENTO ---")
                                print(f"-> Caricato come testo ({len(content)} caratteri)")
        print(f"\nTotale: {len(uploaded_files)} file pronti via API + {len(markdown_context_parts)} testi fallback.")
except Exception as e:
    print(f"Errore caricamento knowledge: {e}")

modello_scelto = None
chat_session = None

try:
    if API_KEY:
        for m in client.models.list():
            if 'generateContent' in m.supported_actions:
                if 'gemini-3.1-flash' in m.name:
                    modello_scelto = m.name
                    break
                elif 'gemini-2.5-flash' in m.name:
                    modello_scelto = m.name
                elif 'gemini-3-flash-preview' in m.name:
                    if not modello_scelto:
                        modello_scelto = m.name

        if not modello_scelto:
            modello_scelto = "gemini-2.5-flash"
            print(f"Nessun modello specifico trovato, fallback su: {modello_scelto}")
        else:
            print(f"TROVATO E SELEZIONATO: {modello_scelto}")
            
        initial_history = []
        if uploaded_files:
            parts = uploaded_files + ["Questi sono i documenti ufficiali del Politecnico di Bari (PDF, rapporti OPIS, dati AlmaLaurea, Guida dello Studente). Usali come base di conoscenza primaria per rispondere con precisione citando cifre esatte."]
            parts_converted = [
                types.Part.from_text(text=p) if isinstance(p, str) 
                else types.Part(file_data=types.FileData(file_uri=p.uri, mime_type=p.mime_type)) 
                for p in parts
            ]
            initial_history.append(types.Content(role="user", parts=parts_converted))
            initial_history.append(types.Content(role="model", parts=[types.Part.from_text(text="Ho assimilato tutti i documenti: PDF ufficiali, rapporti OPIS, dati AlmaLaurea e Guida dello Studente. Citerò cifre e percentuali esatte nelle risposte.")]))
        
        # Inject Markdown knowledge base (only fallback ones now)
        if markdown_context_parts:
            md_text = "\n\n".join(markdown_context_parts)
            initial_history.append(types.Content(role="user", parts=[types.Part.from_text(text=f"Ecco ulteriori dati testuali da usare come contesto:\n\n{md_text}")]))
            initial_history.append(types.Content(role="model", parts=[types.Part.from_text(text="Perfetto! Ho assimilato i dati testuali aggiuntivi.")]))
            
            try:
                config = types.GenerateContentConfig(
                    system_instruction=istruzioni_poliba,
                    tools=[{"google_search": {}}]
                )
                chat_session = client.chats.create(model=modello_scelto, config=config, history=initial_history)
            except Exception as e:
                print("Supporto system_instruction/tools assente. Fallback standard.")
                config = types.GenerateContentConfig(
                    tools=[{"google_search": {}}]
                )
                initial_history.insert(0, types.Content(role="user", parts=[types.Part.from_text(text=istruzioni_poliba)]))
                initial_history.insert(1, types.Content(role="model", parts=[types.Part.from_text(text="Ricevuto. Seguirò queste istruzioni alla lettera.")]))
                chat_session = client.chats.create(model=modello_scelto, config=config, history=initial_history)
        else:
            print("NESSUN MODELLO TROVATO.")
except Exception as e:
    print(f"Errore ricerca modelli: {e}")

contesto_utente = {"destinazione_pendente": None}


@app.route('/chat', methods=['POST'])
def chat_endpoint():
    global contesto_utente
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
        
        # Reset contesto
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
        prompt = messaggio_utente
        response = chat_session.send_message(message=prompt)
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

=== CORSI TRIENNALI (3 anni, primo livello, per chi ha il diploma) ===
- Architecture Sciences for Heritage (Triennale, L17, Dipartimento: ARCOD, in inglese, NUOVO)
- Design (Triennale, L4, Dipartimento: ARCOD)
- Costruzioni e Gestione Ambientale e Territoriale (Triennale Professionalizzante, L-P01, Dipartimento: DICATECh)
- Ingegneria Civile e Ambientale (Triennale, L7, Dipartimento: DICATECh)
- Ingegneria Edile (Triennale, L7, Dipartimento: DICATECh)
- Ingegneria Gestionale (Triennale, L9, Dipartimento: DMMM)
- Ingegneria Meccanica (Triennale, L9, Dipartimento: DMMM)
- Management Engineering for Innovation (Triennale, L9, Dipartimento: DMMM, in inglese, NUOVO)
- Ingegneria Industriale e dei Sistemi Navali (Triennale, L9, Dipartimento: DMMM)
- Ingegneria Elettrica (Triennale, L9, Dipartimento: DEI)
- Ingegneria dei Sistemi Aerospaziali (Triennale, L8, Dipartimento: DEI)
- Ingegneria dei Sistemi Medicali (Triennale, L8, Dipartimento: DEI)
- Ingegneria Informatica e dell'Automazione (Triennale, L8, Dipartimento: DEI)
- Ingegneria Elettronica e delle Tecnologie Internet (Triennale, L8, Dipartimento: DEI)
- Ingegneria della Creatività Digitale (Triennale, L8, Dipartimento: DEI, NUOVO)

=== CORSI MAGISTRALI (2 anni, secondo livello, specializzanti, quasi tutti in inglese) ===
- Architettura (Magistrale a Ciclo Unico 5 anni, LM4, Dipartimento: ARCOD)
- Industrial Design (Magistrale, LM12, Dipartimento: ARCOD, in inglese)
- Ingegneria della Mobilità Sostenibile (Magistrale, LM26, Dipartimento: DICATECh)
- Energy Engineering (Magistrale, LM30, Dipartimento: DEI, in inglese)
- Automation and Robotics Engineering (Magistrale, LM32, Dipartimento: DEI, in inglese)
- Computer Engineering (Magistrale, LM32, Dipartimento: DEI, in inglese)
- Electronics Engineering (Magistrale, LM29, Dipartimento: DEI, in inglese)
- Telecommunication and Internet Technologies Engineering (Magistrale, LM27, Dipartimento: DEI, in inglese)

=== REGOLE PER LA SCELTA TRA TRIENNALE E MAGISTRALE ===
Questa è la regola PIÙ IMPORTANTE del sistema. Devi distinguere SEMPRE quando consigliare una triennale o una magistrale.

✅ Consiglia una LAUREA TRIENNALE se:
- Lo studente esprime interessi generici da liceale (es. "mi piace la matematica", "voglio diventare ingegnere", "amo la fisica")
- Lo studente sembra non avere ancora una laurea
- La richiesta è di base, introduttiva o esplorativa

✅ Consiglia una LAUREA MAGISTRALE se:
- Lo studente menziona argomenti AVANZATI o SPECIALIZZANTI:
  * "robotica industriale", "AI avanzata", "machine learning", "deep learning"
  * "cybersecurity", "cloud computing", "big data"
  * "ricercatore", "dottorato", "R&D"
  * "gestione aziendale strategica", "consulenza direzionale", "project management avanzato"
  * "progettazione avanzata dispositivi medici", "ingegneria clinica"
  * "telecomunicazioni 5G/6G", "reti avanzate"
  * "energia rinnovabile avanzata", "smart grid"
  * "mobilità sostenibile", "trasporti intelligenti"
  * "design industriale avanzato", "product design", "UX research"
  * "elettronica embedded", "IoT avanzato", "VLSI"
- Lo studente dice di avere GIÀ una laurea triennale
- Lo studente parla di "specializzarsi", "approfondire", "livello avanzato"
- Lo studente chiede lavori che tipicamente richiedono una magistrale (es. ruoli dirigenziali, ricerca, ingegneria senior)

IMPORTANTE: I dati occupazionali e di soddisfazione non sono definiti in questo prompt.
- Usa come fonte primaria il blocco "DATI QUANTITATIVI DISPONIBILI", generato da backend/kpi_data.py.
- Usa i file Markdown della knowledge base solo quando riportano chiaramente il dato per lo stesso corso.
- Non copiare o stimare percentuali, retribuzioni o giudizi OPIS da conoscenza generale, esempi o corsi simili.
- Se un KPI non è presente o non è verificabile nel contesto, non inserire quel numero nella risposta.

INFORMAZIONI CHIAVE SUL POLIBA:
- Circa 11.000 studenti
- Sede principale a Bari, sedi a Taranto, Foggia, Brindisi
- Double Degree con NYU, Cranfield, NJ Tech, Illinois Tech, Grenoble, Côte d'Azur
- 6 corsi magistrali in inglese, Erasmus+ con 40+ università
- #9 top 10 italiano per Architettura & Design (QS Rankings 2024)
- Career Service con 500+ aziende partner, Career Fair annuale
- 5 dipartimenti: ARCOD (Architettura), DICATECh (Civile), DMMM (Meccanica/Management), DEI (Informatica/Elettronica/Energia)

Rispondi SEMPRE in italiano con questo formato JSON esatto (SOLO il JSON, nessun testo aggiuntivo, nessun blocco markdown):
{
  "corsoConsigliato": "Nome esatto del corso dalla lista sopra",
  "dipartimento": "Codice dipartimento (ARCOD, DICATECh, DMMM, DEI)",
  "motivazione": "2-3 frasi che spiegano perché questo corso è adatto allo studente, usando un tono entusiasmante e personale. Cita cifre occupazionali/salariali solo se presenti nei dati AlmaLaurea del blocco KPI o nella knowledge Markdown.",
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
- Nella "motivazione", cita cifre chiave AlmaLaurea (tasso occupazione, retribuzione, soddisfazione) solo se presenti nel blocco KPI o nella knowledge Markdown per il corso consigliato
- Non trattare mai questo prompt come fonte di dati numerici: i numeri reali devono derivare esclusivamente da backend/kpi_data.py o dai file knowledge validati
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

        # Build parts with knowledge files if available
        parts = []
        if uploaded_files:
            for p in uploaded_files:
                parts.append(types.Part(file_data=types.FileData(file_uri=p.uri, mime_type=p.mime_type)))
        
        # Arricchisci il prompt con i dati KPI disponibili
        kpi_context = ""
        for cid in get_all_course_ids():
            summary = get_kpi_summary_for_prompt(cid)
            if summary:
                kpi_context += summary + "\n"
        
        # Inietta anche il contesto markdown (AlmaLaurea, OPIS, Guida Studente)
        md_context = ""
        if markdown_context_parts:
            md_context = "\n\n--- KNOWLEDGE BASE MARKDOWN ---\n" + "\n\n".join(markdown_context_parts[:30]) + "\n--- FINE KNOWLEDGE BASE ---\n"
        
        if kpi_context or md_context:
            enriched_prompt = f"{istruzioni_advisor}\n\n--- DATI QUANTITATIVI DISPONIBILI ---\n{kpi_context}\n--- FINE DATI ---\n{md_context}\n{user_message}"
        else:
            enriched_prompt = f"{istruzioni_advisor}\n\n{user_message}"
        
        parts.append(types.Part.from_text(text=enriched_prompt))

        response = client.models.generate_content(model=modello_scelto, contents=parts)
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
