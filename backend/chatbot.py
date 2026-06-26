from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai
from google.genai import types
from dotenv import load_dotenv
from kpi_data import get_kpi, get_all_course_ids, get_kpi_summary_for_prompt, find_course_id_by_name

import json
import logging
import os
import re
import urllib.parse

try:
    import mysql.connector
except ImportError:
    mysql = None


load_dotenv()

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger("poliba-orientamento")

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

API_KEY = os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=API_KEY) if API_KEY else None
if not client:
    logger.warning("GOOGLE_API_KEY assente: /chat e /recommend risponderanno con errore controllato.")


istruzioni_poliba = """
Sei Poliba Orientamento AI PRO, assistente locale dimostrativo per orientamento al Politecnico di Bari.

Regole principali:
1. Rispondi solo su Poliba, universita, orientamento, didattica, servizi e logistica del campus.
2. Usa i documenti forniti tramite Gemini File API come fonte primaria. Questo progetto non usa RAG classica:
   non ci sono embedding, retriever o vector database.
3. Non inventare date, bandi, requisiti o scadenze. Se serve informazione aggiornata, usa Google Search e
   preferisci fonti ufficiali poliba.it. Se l'informazione resta incerta, invita a verificare con gli uffici.
4. Quando parli di corsi, cita se possibile KPI OPIS/AlmaLaurea dai documenti o da kpi_data.py.
5. Le mappe del campus sono un modulo legacy opzionale: se non hai dati mappa, rispondi comunque con testo utile.
6. Rispondi in italiano, con tono chiaro, istituzionale e amichevole.
"""


# =============================================================================
# MAPPE LEGACY / MYSQL OPZIONALE
# =============================================================================
MAPS_ENABLED = os.getenv("ENABLE_LEGACY_MAPS", "1").lower() not in ("0", "false", "no")

INGRESSI = {
    "orabona1": "Orabona1",
    "orabona principale": "Orabona1",
    "via orabona principale": "Orabona1",
    "orabona2": "Orabona2",
    "orabona pedoni": "Orabona2",
    "via orabona pedoni": "Orabona2",
    "redavid": "reDavid",
    "re david": "reDavid",
    "via re david": "reDavid",
    "ulpiani": "ulpiani",
    "celso ulpiani": "ulpiani",
}

MAP_KEY_ALIASES = {
    "ufficio_mongiello_Orabona": "ufficio_mongiello_Orabona1",
    "ufficio_mongiello_orabona1": "ufficio_mongiello_Orabona1",
}

contesto_utente = {"destinazione_pendente": None}


def get_db_connection():
    """Connessione al database mappe legacy.

    Chatbot e Course Advisor non dipendono da MySQL: se XAMPP non e' attivo,
    il modulo mappe fallisce in modo controllato senza bloccare gli endpoint AI.
    """
    if not MAPS_ENABLED:
        return None
    if mysql is None:
        logger.warning("mysql-connector-python non installato: mappe legacy disattivate.")
        return None
    try:
        return mysql.connector.connect(
            host=os.getenv("MYSQL_HOST", "localhost"),
            user=os.getenv("MYSQL_USER", "root"),
            password=os.getenv("MYSQL_PASSWORD", ""),
            database=os.getenv("MYSQL_DATABASE", "poliba_chatbot"),
        )
    except mysql.connector.Error as err:
        logger.warning("MySQL mappe non disponibile: %s", err)
        return None


def get_percorso_from_mysql(chiave_cercata):
    """Legge un percorso legacy senza propagare errori al flusso principale."""
    key = MAP_KEY_ALIASES.get(chiave_cercata, chiave_cercata)
    conn = get_db_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT immagine_url, descrizione FROM mappe WHERE chiave = %s", (key,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        if row:
            return {"img": row["immagine_url"], "desc": row["descrizione"]}
    except Exception as exc:
        logger.exception("Errore query mappe legacy per chiave %s: %s", key, exc)
    return None


def parse_destination(text):
    lower = text.lower()
    if any(k in lower for k in ["biblioteca", "library", "polilibrary"]):
        return "poliLibrary"
    if "mongiello" in lower:
        return "mongiello"
    if any(k in lower for k in ["elettronica", "de venuto", "labddv", "laboratorio ddv"]):
        return "LabDDV"
    return None


def parse_ingresso(text):
    normalized = text.lower().replace("_", " ").replace("-", " ")
    compact = normalized.replace(" ", "")
    for needle, value in INGRESSI.items():
        if needle in normalized or needle.replace(" ", "") in compact:
            return value
    return None


def build_map_key(dest, start):
    if dest == "poliLibrary":
        if start in ("Orabona1", "Orabona2"):
            return "mappa_campus_poliLibrary_Orabona"
        if start == "reDavid":
            return "mappa_campus_poliLibrary_reDavid"
        return "mappa_campus_poliLibrary"
    if dest == "mongiello":
        return f"ufficio_mongiello_{start}"
    if dest == "LabDDV":
        return f"immagine_campus_LabDDV_{start}"
    return None


# =============================================================================
# KNOWLEDGE BASE VIA GEMINI FILE API
# =============================================================================
uploaded_files = []
markdown_context_parts = []
knowledge_items = []

COURSE_HINTS = {
    "informatica": ["informatica", "automazione", "computer"],
    "automazione": ["automazione", "robotics", "robotica"],
    "elettronica": ["elettronica", "electronics", "telecomunicazioni"],
    "gestionale": ["gestionale", "management"],
    "meccanica": ["meccanica", "mechanical"],
    "civile": ["civile", "ambientale", "costruzioni"],
    "edile": ["edile"],
    "elettrica": ["elettrica", "energy"],
    "design": ["design", "creativita", "creativita digitale"],
    "architettura": ["architettura", "architecture"],
    "aerospaziale": ["aerospaziale", "aereospaziale"],
    "medicali": ["medicali", "biomedica", "biomedical"],
}


def infer_knowledge_tags(rel_path):
    lower = rel_path.lower()
    tags = set()
    if "guida" in lower:
        tags.add("guide")
    if "almalaurea" in lower or "occupazionale" in lower:
        tags.add("almalaurea")
    if "opis" in lower or "recensioni" in lower:
        tags.add("opis")
    if "triennale" in lower:
        tags.add("triennale")
    if "magistrale" in lower:
        tags.add("magistrale")
    for tag, hints in COURSE_HINTS.items():
        if any(h in lower for h in hints):
            tags.add(tag)
    return tags


def stable_display_names(rel_path, filename):
    normalized = rel_path.replace(os.sep, "/")
    return urllib.parse.quote(normalized, safe=""), urllib.parse.quote(filename)


def load_knowledge_base():
    """Carica o riusa documenti via Gemini File API.

    Architettura: document-grounded generation con File API. I file vengono
    referenziati direttamente nelle richieste al modello; non ci sono embedding,
    chunk retrieval o vector database.
    """
    if not client:
        return

    existing_files = {}
    try:
        for file_obj in client.files.list():
            display_name = getattr(file_obj, "display_name", None)
            if display_name:
                existing_files[display_name] = file_obj
        logger.info("File API: trovati %s file gia disponibili.", len(existing_files))
    except Exception as exc:
        logger.warning("File API list non disponibile: %s", exc)

    knowledge_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "knowledge")
    if not os.path.exists(knowledge_dir):
        logger.warning("Cartella knowledge non trovata: %s", knowledge_dir)
        return

    for root, _dirs, files in os.walk(knowledge_dir):
        for filename in sorted(files):
            if not filename.lower().endswith((".pdf", ".md", ".json")):
                continue

            filepath = os.path.join(root, filename)
            rel_path = os.path.relpath(filepath, knowledge_dir)
            primary_name, legacy_name = stable_display_names(rel_path, filename)
            lower_name = filename.lower()
            mime = "text/plain" if lower_name.endswith(".md") else None
            if lower_name.endswith(".json"):
                mime = "application/json"

            try:
                file_ref = existing_files.get(primary_name) or existing_files.get(legacy_name)
                if not file_ref:
                    config = {"display_name": primary_name}
                    if mime:
                        config["mime_type"] = mime
                    logger.info("Upload File API: %s", rel_path)
                    file_ref = client.files.upload(file=filepath, config=config)

                uploaded_files.append(file_ref)
                knowledge_items.append({
                    "rel_path": rel_path,
                    "tags": infer_knowledge_tags(rel_path),
                    "file_ref": file_ref,
                    "fallback_text": None,
                })
            except Exception as exc:
                logger.warning("Upload File API fallito per %s: %s", rel_path, exc)
                if lower_name.endswith((".md", ".json")):
                    try:
                        with open(filepath, "r", encoding="utf-8") as handle:
                            content = handle.read()
                        fallback = f"--- DOCUMENTO: {rel_path} ---\n{content}\n--- FINE DOCUMENTO ---"
                        markdown_context_parts.append(fallback)
                        knowledge_items.append({
                            "rel_path": rel_path,
                            "tags": infer_knowledge_tags(rel_path),
                            "file_ref": None,
                            "fallback_text": fallback,
                        })
                    except Exception as read_exc:
                        logger.warning("Fallback testuale fallito per %s: %s", rel_path, read_exc)

    logger.info(
        "Knowledge pronta: %s file File API, %s fallback testuali.",
        len(uploaded_files),
        len(markdown_context_parts),
    )


def select_knowledge_items(message, purpose="chat", limit=10):
    """Intent routing leggero.

    Questa euristica sceglie pochi documenti utili per ridurre latenza e contesto.
    Non e' RAG classica: non calcola embedding e non interroga un vector database.
    """
    if not knowledge_items:
        return []

    text = (message or "").lower()
    wanted_tags = set()
    if any(k in text for k in ["tolc", "iscrizion", "tass", "cfu", "bando", "erasmus", "segreteria", "guida"]):
        wanted_tags.add("guide")
    if any(k in text for k in ["lavor", "occupazione", "stipend", "almalaurea", "retribuzione"]):
        wanted_tags.add("almalaurea")
    if any(k in text for k in ["opinione", "opis", "studenti", "soddisfazione", "docenti"]):
        wanted_tags.add("opis")
    if any(k in text for k in ["magistrale", "specializz", "gia laureato"]):
        wanted_tags.add("magistrale")
    if any(k in text for k in ["triennale", "diploma", "liceo", "scuola"]):
        wanted_tags.add("triennale")
    if purpose == "recommend":
        wanted_tags.update({"almalaurea", "opis"})

    for tag, hints in COURSE_HINTS.items():
        if any(h in text for h in hints):
            wanted_tags.add(tag)

    tokens = [token for token in re.findall(r"[a-zA-Z0-9]+", text) if len(token) > 3]
    scored = []
    for item in knowledge_items:
        rel_lower = item["rel_path"].lower()
        score = len(item["tags"] & wanted_tags) * 5
        score += sum(1 for token in tokens if token in rel_lower)
        if "guide" in item["tags"]:
            score += 1
        if purpose == "recommend" and ("almalaurea" in item["tags"] or "opis" in item["tags"]):
            score += 2
        scored.append((score, item))

    selected = [item for score, item in sorted(scored, key=lambda row: row[0], reverse=True) if score > 0]
    if not selected:
        selected = [item for item in knowledge_items if "guide" in item["tags"]][:2]
    return selected[:limit]


def build_context_parts(message, purpose="chat", limit=10):
    parts = []
    selected = select_knowledge_items(message, purpose=purpose, limit=limit)
    for item in selected:
        file_ref = item.get("file_ref")
        if file_ref:
            parts.append(types.Part(file_data=types.FileData(file_uri=file_ref.uri, mime_type=file_ref.mime_type)))
        elif item.get("fallback_text"):
            parts.append(types.Part.from_text(text=item["fallback_text"]))
    logger.info("Contesto %s: %s documenti selezionati.", purpose, len(selected))
    return parts


def select_model():
    if not client:
        return None
    selected = None
    try:
        for model in client.models.list():
            if "generateContent" not in model.supported_actions:
                continue
            if "gemini-3.1-flash" in model.name:
                return model.name
            if "gemini-2.5-flash" in model.name:
                selected = model.name
            elif "gemini-3-flash-preview" in model.name and not selected:
                selected = model.name
    except Exception as exc:
        logger.warning("Lista modelli Gemini non disponibile: %s", exc)
    return selected or ("gemini-2.5-flash" if client else None)


def generate_with_gemini(user_prompt, system_instruction, purpose="chat", context_limit=10, use_search=True):
    """Generazione stateless con documenti File API selezionati per richiesta."""
    if not client or not modello_scelto:
        raise RuntimeError("Modello Gemini non disponibile")

    parts = build_context_parts(user_prompt, purpose=purpose, limit=context_limit)
    parts.append(types.Part.from_text(text=user_prompt))

    config_kwargs = {"system_instruction": system_instruction}
    if use_search:
        config_kwargs["tools"] = [{"google_search": {}}]

    try:
        config = types.GenerateContentConfig(**config_kwargs)
        return client.models.generate_content(model=modello_scelto, contents=parts, config=config)
    except TypeError:
        logger.warning("GenerateContentConfig non supporta tutti i parametri: fallback senza tool.")
        return client.models.generate_content(model=modello_scelto, contents=parts)


load_knowledge_base()
modello_scelto = select_model()
if modello_scelto:
    logger.info("Modello Gemini selezionato: %s", modello_scelto)
else:
    logger.warning("Nessun modello Gemini disponibile.")


# =============================================================================
# CHATBOT
# =============================================================================
INFOGRAFICA_KEYWORDS = [
    (["informatica", "automazione"], "IIA"),
    (["creativita digitale"], "ICD"),
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
    (["costruzioni", "l-p01", "lp01", "laurea politecnica"], "LPOL"),
]


@app.route("/chat", methods=["POST"])
def chat_endpoint():
    data = request.get_json(silent=True) or {}
    messaggio_utente = (data.get("message") or "").strip()
    if not messaggio_utente:
        return jsonify({"error": "Messaggio vuoto"}), 400

    logger.info("[CHAT] Domanda ricevuta: %s", messaggio_utente[:200])
    messaggio_lower = messaggio_utente.lower()

    if any(k in messaggio_lower for k in ["dove", "dov'e", "dov'e'", "posizione", "come arrivo", "raggiungo"]):
        destinazione = parse_destination(messaggio_utente)
        if destinazione:
            contesto_utente["destinazione_pendente"] = destinazione
            return jsonify({
                "response": f"Per raggiungere {destinazione}, da quale ingresso accedi?",
                "type": "options",
                "options": [
                    {"label": "Via Orabona (Principale)", "value": "Orabona1"},
                    {"label": "Via Orabona (Pedoni)", "value": "Orabona2"},
                    {"label": "Via Re David", "value": "reDavid"},
                    {"label": "Via Celso Ulpiani", "value": "ulpiani"},
                ],
            })

    ingresso_trovato = parse_ingresso(messaggio_utente)
    destinazione_salvata = contesto_utente.get("destinazione_pendente")
    if ingresso_trovato and destinazione_salvata:
        chiave_db = build_map_key(destinazione_salvata, ingresso_trovato)
        logger.info("[MAPPE] Cerco chiave legacy: %s", chiave_db)
        contesto_utente["destinazione_pendente"] = None

        percorso_data = get_percorso_from_mysql(chiave_db) if chiave_db else None
        if percorso_data:
            return jsonify({
                "response": percorso_data["desc"],
                "type": "map",
                "mapUrl": percorso_data["img"],
                "mapTitle": f"Percorso per {destinazione_salvata}",
            })
        return jsonify({
            "response": (
                "Non ho trovato una mappa legacy funzionante per questo percorso. "
                "Il chatbot resta disponibile: posso comunque darti indicazioni testuali sul campus."
            ),
            "type": "text",
        })

    if messaggio_lower in ["mostra infografica", "infografica", "mostrami l'infografica", "voglio vedere l'infografica"]:
        return jsonify({
            "response": "Dimmi il nome del corso, per esempio: Mostra infografica Ingegneria Gestionale.",
            "type": "text",
        })

    if not modello_scelto:
        return jsonify({"error": "Errore AI: modello non disponibile"}), 500

    try:
        response = generate_with_gemini(messaggio_utente, istruzioni_poliba, purpose="chat", context_limit=8)
        testo_risposta = (response.text or "").strip()
        testo_lower = testo_risposta.lower()
        infografica_id = None
        for keywords, candidate_id in INFOGRAFICA_KEYWORDS:
            if any(keyword in testo_lower for keyword in keywords):
                infografica_id = candidate_id
                break

        payload = {
            "response": testo_risposta,
            "type": "text",
            "options": [],
        }
        if infografica_id:
            payload["infograficaId"] = infografica_id
        return jsonify(payload)
    except Exception as exc:
        errore = str(exc)
        logger.exception("[CHAT] Errore AI: %s", errore)
        if "429" in errore:
            return jsonify({"response": "Troppe richieste. Riprova tra poco.", "type": "text"}), 200
        return jsonify({"response": "Errore AI durante la generazione della risposta.", "type": "text"}), 500


# =============================================================================
# ANALISI KPI
# =============================================================================
@app.route("/analysis", methods=["GET"])
def analysis_endpoint():
    """Restituisce i KPI strutturati per un dato course_id da kpi_data.py."""
    course_id = request.args.get("course_id", "").strip().upper()
    if not course_id:
        return jsonify({
            "error": "Parametro 'course_id' mancante.",
            "available_ids": get_all_course_ids(),
        }), 400

    data = get_kpi(course_id)
    if not data:
        return jsonify({
            "error": f"Corso '{course_id}' non trovato nel database KPI.",
            "available_ids": get_all_course_ids(),
        }), 404
    return jsonify(data)


# =============================================================================
# COURSE ADVISOR
# =============================================================================
istruzioni_advisor = """
Sei un orientatore universitario esperto del Politecnico di Bari.
Raccomanda un solo corso tra quelli del Poliba, distinguendo con attenzione triennale e magistrale.

Usa kpi_data.py e i documenti File API come contesto quantitativo. Le percentuali in areeInteresse servono
solo per il radar chart UI: sono stime generate dal modello sull'affinita percepita, non uno scoring
deterministico e non una misura ufficiale.

Rispondi solo con JSON valido, senza markdown, con questo schema:
{
  "corsoConsigliato": "Nome corso",
  "dipartimento": "ARCOD|DICATECh|DMMM|DEI",
  "motivazione": "2-3 frasi con almeno un dato KPI se disponibile",
  "puntiForza": ["punto 1", "punto 2", "punto 3"],
  "sbocchiLavorativi": ["sbocco 1", "sbocco 2", "sbocco 3"],
  "opportunitaInternazionali": "testo breve",
  "corsiAlternativi": ["corso 1", "corso 2"],
  "consiglio": "testo breve",
  "areeInteresse": [
    {"nome": "Area 1", "percentuale": 85},
    {"nome": "Area 2", "percentuale": 70},
    {"nome": "Area 3", "percentuale": 60},
    {"nome": "Area 4", "percentuale": 50},
    {"nome": "Area 5", "percentuale": 40},
    {"nome": "Area 6", "percentuale": 30}
  ]
}
"""


def extract_json_object(response_text):
    """Estrae JSON anche se il modello aggiunge accidentalmente fence markdown o testo."""
    text = (response_text or "").strip()
    fence_match = re.search(r"```(?:json)?\s*(.*?)```", text, flags=re.IGNORECASE | re.DOTALL)
    if fence_match:
        text = fence_match.group(1).strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(text[start:end + 1])
        raise


def normalize_advisor_payload(parsed):
    required = [
        "corsoConsigliato",
        "dipartimento",
        "motivazione",
        "puntiForza",
        "sbocchiLavorativi",
        "opportunitaInternazionali",
        "corsiAlternativi",
        "consiglio",
        "areeInteresse",
    ]
    missing = [key for key in required if key not in parsed]
    if missing:
        raise ValueError(f"Campi JSON mancanti: {', '.join(missing)}")

    areas = parsed.get("areeInteresse")
    if not isinstance(areas, list) or not areas:
        raise ValueError("areeInteresse deve essere una lista non vuota")

    normalized_areas = []
    for area in areas[:6]:
        nome = str(area.get("nome", "Area")).strip() or "Area"
        try:
            percentuale = int(float(area.get("percentuale", 0)))
        except (TypeError, ValueError):
            percentuale = 0
        normalized_areas.append({
            "nome": nome,
            "percentuale": max(0, min(100, percentuale)),
        })

    while len(normalized_areas) < 6:
        normalized_areas.append({"nome": f"Area {len(normalized_areas) + 1}", "percentuale": 0})

    parsed["areeInteresse"] = normalized_areas
    parsed["radarChartNote"] = "Percentuali generate dal modello; non scoring deterministico."
    return parsed


def advisor_parse_error(message, raw_text=""):
    return jsonify({
        "error": "La risposta AI non era JSON valido per il Course Advisor.",
        "detail": message,
        "rawResponsePreview": (raw_text or "")[:700],
        "expectedShape": [
            "corsoConsigliato",
            "dipartimento",
            "motivazione",
            "puntiForza",
            "sbocchiLavorativi",
            "opportunitaInternazionali",
            "corsiAlternativi",
            "consiglio",
            "areeInteresse",
        ],
    }), 502


@app.route("/recommend", methods=["POST"])
def recommend_endpoint():
    data = request.get_json(silent=True) or {}
    materie = data.get("materie", [])
    aspirazioni = data.get("aspirazioni", [])
    note = data.get("note", "")

    if not materie and not aspirazioni:
        return jsonify({"error": "Inserisci almeno una materia o un'aspirazione"}), 400
    if not modello_scelto:
        return jsonify({"error": "Modello AI non disponibile"}), 500

    logger.info("[ADVISOR] Materie=%s Aspirazioni=%s", materie, aspirazioni)

    kpi_context = ""
    for course_id in get_all_course_ids():
        summary = get_kpi_summary_for_prompt(course_id)
        if summary:
            kpi_context += summary + "\n"

    user_profile = f"""Materie preferite: {', '.join(materie) if materie else 'non specificate'}
Aspirazioni lavorative: {', '.join(aspirazioni) if aspirazioni else 'non specificate'}
Note aggiuntive: {note if note else 'nessuna'}"""

    prompt = f"""{istruzioni_advisor}

--- KPI DISPONIBILI DA kpi_data.py ---
{kpi_context}
--- FINE KPI ---

Profilo studente:
{user_profile}

Restituisci il JSON valido della raccomandazione."""

    response_text = ""
    try:
        response = generate_with_gemini(prompt, istruzioni_advisor, purpose="recommend", context_limit=12, use_search=False)
        response_text = (response.text or "").strip()
        parsed = normalize_advisor_payload(extract_json_object(response_text))

        corso_consigliato = parsed.get("corsoConsigliato", "")
        course_id = find_course_id_by_name(corso_consigliato)
        if course_id:
            kpi = get_kpi(course_id)
            if kpi:
                parsed["kpiData"] = kpi
                parsed["courseKpiId"] = course_id

        return jsonify(parsed)
    except json.JSONDecodeError as exc:
        logger.warning("[ADVISOR] JSON non valido: %s", exc)
        return advisor_parse_error(str(exc), response_text)
    except ValueError as exc:
        logger.warning("[ADVISOR] JSON incompleto: %s", exc)
        return advisor_parse_error(str(exc), response_text)
    except Exception as exc:
        errore = str(exc)
        logger.exception("[ADVISOR] Errore: %s", errore)
        if "429" in errore:
            return jsonify({"error": "Troppe richieste. Riprova tra poco."}), 429
        return jsonify({"error": "Errore nella raccomandazione AI", "detail": errore[:300]}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
