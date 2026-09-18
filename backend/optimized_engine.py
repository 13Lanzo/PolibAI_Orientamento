import os
import re
import json
import time
import math
from typing import List, Dict, Any, Optional, Tuple
from collections import Counter
from dotenv import load_dotenv

# Carica env
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

from kpi_data import get_kpi, get_all_course_ids, get_kpi_summary_for_prompt, find_course_id_by_name, COURSE_KPI

# =============================================================================
# 1. KNOWLEDGE CHUNKER & INDEXER
# =============================================================================

class KnowledgeIndexer:
    def __init__(self, knowledge_dir: str, cache_file: Optional[str] = None):
        self.knowledge_dir = knowledge_dir
        self.cache_file = cache_file or os.path.join(os.path.dirname(os.path.abspath(__file__)), "knowledge_index_cache.json")
        self.chunks: List[Dict[str, Any]] = []
        self.doc_registry: Dict[str, Dict[str, Any]] = {}
        self._build_or_load_index()

    def _extract_pdf_text(self, filepath: str) -> List[Tuple[int, str]]:
        pages_content = []
        try:
            import pypdf
            reader = pypdf.PdfReader(filepath)
            for i, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                if text.strip():
                    pages_content.append((i + 1, text))
        except Exception as e:
            print(f"[INDEXER] Errore lettura PDF {filepath}: {e}")
        return pages_content

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\b[a-zA-Z0-9àèéìòùáéíóú]{2,}\b', text.lower())

    def _build_or_load_index(self):
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.chunks = data.get("chunks", [])
                    self.doc_registry = data.get("doc_registry", {})
                    print(f"[INDEXER] Caricati {len(self.chunks)} chunk indicizzati da cache ({len(self.doc_registry)} documenti).")
                    return
            except Exception as e:
                print(f"[INDEXER] Cache non valida, rigenerazione: {e}")

        print(f"[INDEXER] Indicizzazione documenti da {self.knowledge_dir}...")
        self.chunks = []
        self.doc_registry = {}
        chunk_id = 0

        for root, _, files in os.walk(self.knowledge_dir):
            for filename in sorted(files):
                filepath = os.path.join(root, filename)
                rel_path = os.path.relpath(filepath, self.knowledge_dir).replace("\\", "/")
                ext = os.path.splitext(filename)[1].lower()

                self.doc_registry[rel_path] = {
                    "filename": filename,
                    "rel_path": rel_path,
                    "extension": ext,
                    "size": os.path.getsize(filepath)
                }

                if ext in [".md", ".txt"]:
                    try:
                        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read()
                        
                        # Dividi per intestazioni markdown o paragrafi
                        sections = re.split(r'\n(?=#{1,4}\s)', content)
                        for sec in sections:
                            sec = sec.strip()
                            if not sec:
                                continue
                            # Se troppo lunga, suddividi ulteriormente
                            paragraphs = sec.split("\n\n")
                            current_buf = []
                            current_len = 0
                            for p in paragraphs:
                                current_buf.append(p)
                                current_len += len(p)
                                if current_len > 1200:
                                    chunk_text = "\n\n".join(current_buf)
                                    self.chunks.append({
                                        "chunk_id": chunk_id,
                                        "doc_path": rel_path,
                                        "doc_name": filename,
                                        "text": chunk_text,
                                        "tokens": self._tokenize(chunk_text)
                                    })
                                    chunk_id += 1
                                    current_buf = []
                                    current_len = 0
                            if current_buf:
                                chunk_text = "\n\n".join(current_buf)
                                self.chunks.append({
                                    "chunk_id": chunk_id,
                                    "doc_path": rel_path,
                                    "doc_name": filename,
                                    "text": chunk_text,
                                    "tokens": self._tokenize(chunk_text)
                                })
                                chunk_id += 1
                    except Exception as e:
                        print(f"[INDEXER] Errore lettura {rel_path}: {e}")

                elif ext == ".pdf":
                    pages = self._extract_pdf_text(filepath)
                    for page_num, text in pages:
                        # Chunk per pagina o mezza pagina
                        paragraphs = text.split("\n\n")
                        current_buf = []
                        current_len = 0
                        for p in paragraphs:
                            current_buf.append(p)
                            current_len += len(p)
                            if current_len > 1000:
                                chunk_text = f"[Pagina {page_num}] " + "\n".join(current_buf)
                                self.chunks.append({
                                    "chunk_id": chunk_id,
                                    "doc_path": rel_path,
                                    "doc_name": filename,
                                    "page": page_num,
                                    "text": chunk_text,
                                    "tokens": self._tokenize(chunk_text)
                                })
                                chunk_id += 1
                                current_buf = []
                                current_len = 0
                        if current_buf:
                            chunk_text = f"[Pagina {page_num}] " + "\n".join(current_buf)
                            self.chunks.append({
                                "chunk_id": chunk_id,
                                "doc_path": rel_path,
                                "doc_name": filename,
                                "page": page_num,
                                "text": chunk_text,
                                "tokens": self._tokenize(chunk_text)
                            })
                            chunk_id += 1

                elif ext == ".json":
                    try:
                        with open(filepath, "r", encoding="utf-8") as f:
                            jsdata = json.load(f)
                        text = json.dumps(jsdata, ensure_ascii=False, indent=2)
                        # Salva blocchi di 1500 caratteri
                        lines = text.split("\n")
                        for i in range(0, len(lines), 50):
                            block = "\n".join(lines[i:i+50])
                            self.chunks.append({
                                "chunk_id": chunk_id,
                                "doc_path": rel_path,
                                "doc_name": filename,
                                "text": block,
                                "tokens": self._tokenize(block)
                            })
                            chunk_id += 1
                    except Exception as e:
                        print(f"[INDEXER] Errore lettura JSON {rel_path}: {e}")

        # Salva in cache
        try:
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump({"chunks": self.chunks, "doc_registry": self.doc_registry}, f, ensure_ascii=False, indent=2)
            print(f"[INDEXER] Indicizzati {len(self.chunks)} chunk da {len(self.doc_registry)} documenti. Salvato in {self.cache_file}")
        except Exception as e:
            print(f"[INDEXER] Errore salvataggio cache: {e}")


# =============================================================================
# 2. SELECTIVE RETRIEVER (BM25 / TF-IDF RANKER)
# =============================================================================

class SelectiveRetriever:
    def __init__(self, indexer: KnowledgeIndexer):
        self.indexer = indexer
        self.chunks = indexer.chunks
        self.doc_count = len(self.chunks)
        self.avg_doc_len = sum(len(c["tokens"]) for c in self.chunks) / max(1, self.doc_count)
        self.df = Counter()
        for c in self.chunks:
            unique_tokens = set(c["tokens"])
            for t in unique_tokens:
                self.df[t] += 1
        self.k1 = 1.5
        self.b = 0.75

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        query_tokens = self.indexer._tokenize(query)
        if not query_tokens:
            return []

        scores = []
        for c in self.chunks:
            tokens = c["tokens"]
            doc_len = len(tokens)
            if doc_len == 0:
                continue
            tf = Counter(tokens)
            score = 0.0

            for t in query_tokens:
                if t in tf:
                    doc_freq = self.df.get(t, 0)
                    # BM25 IDF con smoothing
                    idf = math.log((self.doc_count - doc_freq + 0.5) / (doc_freq + 0.5) + 1.0)
                    term_tf = tf[t]
                    numerator = term_tf * (self.k1 + 1)
                    denominator = term_tf + self.k1 * (1 - self.b + self.b * (doc_len / self.avg_doc_len))
                    score += idf * (numerator / denominator)

            # Bonus se il nome del documento matcha la query
            doc_name_lower = c["doc_name"].lower()
            for t in query_tokens:
                if len(t) > 3 and t in doc_name_lower:
                    score += 2.0

            if score > 0.05:
                scores.append((score, c))

        scores.sort(key=lambda x: x[0], reverse=True)
        top_results = []
        for rank, (score, c) in enumerate(scores[:top_k], start=1):
            top_results.append({
                "rank": rank,
                "score": round(score, 4),
                "chunk_id": c["chunk_id"],
                "doc_name": c["doc_name"],
                "doc_path": c["doc_path"],
                "text": c["text"]
            })
        return top_results


# =============================================================================
# 3. SESSION MANAGER (Isolamento Multiutenza)
# =============================================================================

class SessionManager:
    def __init__(self, max_history_turns: int = 10):
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.max_history_turns = max_history_turns

    def get_session(self, session_id: str) -> Dict[str, Any]:
        if not session_id or session_id not in self.sessions:
            sid = session_id or f"sess_{int(time.time()*1000)}"
            self.sessions[sid] = {
                "id": sid,
                "history": [],
                "user_state": {"destinazione_pendente": None},
                "created_at": time.time(),
                "last_active": time.time()
            }
            return self.sessions[sid]
        
        self.sessions[session_id]["last_active"] = time.time()
        return self.sessions[session_id]

    def append_history(self, session_id: str, role: str, message: str):
        sess = self.get_session(session_id)
        sess["history"].append({"role": role, "content": message, "timestamp": time.time()})
        if len(sess["history"]) > self.max_history_turns * 2:
            sess["history"] = sess["history"][-self.max_history_turns * 2:]

    def clear_session(self, session_id: str):
        if session_id in self.sessions:
            del self.sessions[session_id]


# =============================================================================
# 4. PROMPT ADVISOR E OPTIMIZED ENGINE
# =============================================================================

ISTRUZIONI_ADVISOR = """
Sei un orientatore universitario esperto del Politecnico di Bari (Poliba). Il tuo compito è analizzare gli interessi e le aspirazioni lavorative di uno studente e raccomandare il corso di laurea più adatto tra quelli offerti dal Poliba.

Ecco i corsi disponibili al Poliba (A.A. 2024-2025):
=== CORSI TRIENNALI ===
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

=== CORSI MAGISTRALI ===
- Architettura (Magistrale a Ciclo Unico 5 anni, LM4, Dipartimento: ARCOD)
- Industrial Design (Magistrale, LM12, Dipartimento: ARCOD, in inglese)
- Ingegneria della Mobilità Sostenibile (Magistrale, LM26, Dipartimento: DICATECh)
- Energy Engineering (Magistrale, LM30, Dipartimento: DEI, in inglese)
- Automation and Robotics Engineering (Magistrale, LM32, Dipartimento: DEI, in inglese)
- Computer Engineering (Magistrale, LM32, Dipartimento: DEI, in inglese)
- Electronics Engineering (Magistrale, LM29, Dipartimento: DEI, in inglese)
- Telecommunication and Internet Technologies Engineering (Magistrale, LM27, Dipartimento: DEI, in inglese)

=== REGOLE SCELTA TRIENNALE vs MAGISTRALE ===
- Consiglia TRIENNALE se studente con diploma o interessi base.
- Consiglia MAGISTRALE se studente con laurea triennale o argomenti specialistici (AI avanzata, robotica industriale, big data, smart grid, eco-design avanzato).

Rispondi SEMPRE ed ESCLUSIVAMENTE con un JSON valido strutturato esattamente così:
{
  "corsoConsigliato": "Nome esatto del corso dalla lista",
  "dipartimento": "Codice dipartimento (ARCOD, DICATECh, DMMM, DEI)",
  "motivazione": "2-3 frasi convincenti e personalizzate",
  "puntiForza": ["punto 1", "punto 2", "punto 3"],
  "sbocchiLavorativi": ["sbocco 1", "sbocco 2", "sbocco 3"],
  "opportunitaInternazionali": "Descrizione breve delle opportunità internazionali",
  "corsiAlternativi": ["Alternativa 1", "Alternativa 2"],
  "consiglio": "Un consiglio motivazionale personale",
  "areeInteresse": [
    {"nome": "Area 1", "percentuale": 85},
    {"nome": "Area 2", "percentuale": 70},
    {"nome": "Area 3", "percentuale": 60},
    {"nome": "Area 4", "percentuale": 50},
    {"nome": "Area 5", "percentuale": 40},
    {"nome": "Area 6", "percentuale": 30}
  ]
}
IMPORTANTE: Il campo 'areeInteresse' è OBBLIGATORIO e deve contenere esattamente 6 aree con percentuale intera da 0 a 100 per il radar chart.
"""

ISTRUZIONI_CHAT_POLIBA = """
# [RUOLO E IDENTITÀ]
Sei "PolibAI Orientamento AI PRO", l'Assistente Virtuale Ufficiale per l'orientamento, la didattica e i servizi del Politecnico di Bari (POLIBA).
Il tuo compito è guidare futuri studenti, iscritti e visitatori. Rispondi con un tono cordiale, istituzionale ma giovanile, empatico ed entusiasta. Dai sempre del "tu" allo studente.
Usa una formattazione Markdown chiara ed elegante (grassetto per i concetti chiave, elenchi puntati ed emoji tematiche coerenti: 🎓, 📍, 💡, 📅, 📊).

=== OFFERTA FORMATIVA UFFICIALE DEL POLITECNICO DI BARI ===
--- LAUREE TRIENNALI (3 ANNI - PRIMO LIVELLO) ---
Dipartimento di Ingegneria Elettrica e dell'Informazione (DEI):
- Ingegneria Informatica e dell'Automazione (L-8)
- Ingegneria Elettronica e delle Tecnologie Internet (L-8)
- Ingegneria dei Sistemi Medicali (L-8)
- Ingegneria dei Sistemi Aerospaziali (L-8, sede Taranto e Bari)
- Ingegneria della Creatività Digitale (L-8, Nuovo corso interdisciplinare)
- Ingegneria Elettrica (L-9)

Dipartimento di Meccanica, Matematica e Management (DMMM):
- Ingegneria Gestionale (L-9)
- Ingegneria Meccanica (L-9)
- Management Engineering for Innovation (L-9, in lingua inglese, Nuovo corso)
- Ingegneria Industriale e dei Sistemi Navali (L-9, sede Taranto)

Dipartimento di Ingegneria Civile, Ambientale, del Territorio, Edile e di Chimica (DICATECh):
- Ingegneria Civile e Ambientale (L-7)
- Ingegneria Edile (L-7)
- Costruzioni e Gestione Ambientale e Territoriale (L-P01, Laurea ad orientamento professionale)

Dipartimento di Architettura, Costruzione e Design (ARCOD):
- Design (L-4, Disegno Industriale)
- Architecture Sciences for Heritage (L-17, in lingua inglese, Nuovo corso)

--- LAUREE MAGISTRALI (2 ANNI / CICLO UNICO) ---
- Architettura (LM-4 c.u., Ciclo Unico 5 anni)
- Industrial Design (LM-12, in inglese)
- Ingegneria della Mobilità Sostenibile (LM-26)
- Energy Engineering (LM-30, in inglese)
- Automation and Robotics Engineering (LM-32, in inglese)
- Computer Engineering (LM-32, in inglese)
- Electronics Engineering (LM-29, in inglese)
- Telecommunication and Internet Technologies Engineering (LM-27, in inglese)
- Ingegneria Gestionale (LM-31)
- Ingegneria Meccanica (LM-33)
- Ingegneria Civile (LM-23)
- Ingegneria Elettrica (LM-28)

=== REGOLE OPERATIVE ===
1. Quando l'utente chiede quali corsi sono disponibili (triennali o magistrali), elenca con chiarezza e precisione i corsi ufficiali sopra riportati, raggruppandoli per area disciplinare o dipartimento per facilitare la lettura.
2. Integra le risposte con le informazioni estratte dai documenti ufficiali forniti nel contesto (tasse, scadenze, requisiti CFU, AlmaLaurea, OPIS).
3. Se l'utente chiede informazioni in tempo reale su avvisi recenti, scadenze TOLC o bandi di immatricolazione, puoi utilizzare la ricerca web integrata sul sito "poliba.it".
4. Mantieni sempre uno stile accogliente e incoraggiante.
"""

class OptimizedPolibAIEngine:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.client = None
        if self.api_key and GENAI_AVAILABLE:
            self.client = genai.Client(api_key=self.api_key)
        
        knowledge_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "knowledge")
        self.indexer = KnowledgeIndexer(knowledge_dir)
        self.retriever = SelectiveRetriever(self.indexer)
        self.session_manager = SessionManager()
        self.model_name = "gemini-2.5-flash"

    def route_intent(self, message: str) -> str:
        """Classifica l'intento per evitare chiamate LLM ridondanti o selezionare la fonte esatta."""
        msg_lower = message.lower()
        if any(w in msg_lower for w in ["consigliami un corso", "quale corso scegliere", "mi piace la matematica e", "aspirazioni lavorative", "orientamento"]):
            return "COURSE_ADVISOR"
        if any(w in msg_lower for w in ["retribuzione", "tasso di occupazione", "giudizi opis", "soddisfazione laureati", "kpi"]):
            return "KPI_SPECIFIC"
        return "GENERAL_RAG"

    def process_chat_optimized(self, message: str, session_id: str = "default_user", top_k: int = 5) -> Dict[str, Any]:
        t0 = time.perf_counter()
        session = self.session_manager.get_session(session_id)
        intent = self.route_intent(message)
        t1 = time.perf_counter()

        # Selective Retrieval top-k
        retrieved_chunks = self.retriever.search(message, top_k=top_k)
        t2 = time.perf_counter()

        # Costruzione del contesto compatto
        context_snippets = []
        for rc in retrieved_chunks:
            context_snippets.append(f"--- Fonte: {rc['doc_name']} (Rilevanza: {rc['score']}) ---\n{rc['text']}")
        context_text = "\n\n".join(context_snippets)

        # Se la domanda cita un corso specifico, allega solo i KPI di quel corso
        course_id = None
        for cid, cdata in COURSE_KPI.items():
            if cdata["nome"].lower() in message.lower() or cid.lower() in message.lower():
                course_id = cid
                break
        
        kpi_snippet = ""
        if course_id:
            kpi_snippet = f"\n[KPI UFFICIALI CORSO {course_id}]:\n" + get_kpi_summary_for_prompt(course_id)

        system_instruction = (
            f"{ISTRUZIONI_CHAT_POLIBA}\n\n"
            f"[ESTRATTI DOCUMENTALI SELEZIONATI DALLA KNOWLEDGE BASE (TOP-{top_k})]:\n"
            f"{context_text}\n"
            f"{kpi_snippet}\n\n"
            "Rispondi in modo esaustivo, cordiale e accattivante, integrando l'offerta formativa ufficiale e gli estratti forniti."
        )

        prompt = message
        input_tokens = 0
        output_tokens = 0
        response_text = ""

        try:
            if self.client:
                config = types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.3,
                    tools=[{"google_search": {}}]
                )
                res = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=config
                )
                response_text = res.text or ""
                if hasattr(res, "usage_metadata") and res.usage_metadata:
                    input_tokens = getattr(res.usage_metadata, "prompt_token_count", 0) or 0
                    output_tokens = getattr(res.usage_metadata, "candidates_token_count", 0) or 0
            else:
                response_text = "Modalità offline: risposta simulata."
        except Exception as e:
            response_text = f"Errore generazione: {e}"

        t3 = time.perf_counter()

        # C. Post-processing
        self.session_manager.append_history(session_id, "user", message)
        self.session_manager.append_history(session_id, "model", response_text)
        t4 = time.perf_counter()
        t5 = time.perf_counter()

        retrieved_doc_names = list(dict.fromkeys([rc["doc_name"] for rc in retrieved_chunks]))

        return {
            "response": response_text,
            "type": "text",
            "telemetry": {
                "t0": t0, "t1": t1, "t2": t2, "t3": t3, "t4": t4, "t5": t5,
                "t_network_pre_ms": round((t1 - t0) * 1000, 2),
                "t_retrieval_ms": round((t2 - t1) * 1000, 2),
                "t_llm_ms": round((t3 - t2) * 1000, 2),
                "t_post_ms": round((t4 - t3) * 1000, 2),
                "t_total_ms": round((t5 - t0) * 1000, 2),
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens,
                "intent": intent,
                "top_k": top_k,
                "retrieved_docs": retrieved_doc_names,
                "retrieved_chunks": [
                    {"doc_name": rc["doc_name"], "score": rc["score"], "rank": rc["rank"]}
                    for rc in retrieved_chunks
                ]
            }
        }

    def process_recommend_optimized(self, materie: List[str], aspirazioni: List[str], note: str = "") -> Dict[str, Any]:
        """Versione ottimizzata di /recommend: invia solo l'elenco compatto dei corsi e i KPI sintetici, riducendo i token da 263k a ~3k."""
        t0 = time.perf_counter()
        t1 = time.perf_counter()

        query_hint = " ".join(materie + aspirazioni + [note])
        
        # Retrieval selettivo di soli 3 documenti/chunk mirati sui corsi affini
        relevant_chunks = self.retriever.search(query_hint, top_k=3)
        t2 = time.perf_counter()

        kb_context = "\n".join([f"Fonte {rc['doc_name']}: {rc['text'][:400]}" for rc in relevant_chunks])

        user_message = (
            f"Materie dello studente: {', '.join(materie) if materie else 'non indicate'}\n"
            f"Aspirazioni dello studente: {', '.join(aspirazioni) if aspirazioni else 'non indicate'}\n"
            f"Note: {note}\n"
            "Analizza il profilo e restituisci il JSON con il corso consigliato e le 6 areeInteresse per il radar chart."
        )

        prompt = f"{ISTRUZIONI_ADVISOR}\n\n[CONTESTO SELETTIVO RIDOTTO]:\n{kb_context}\n\n{user_message}"

        input_tokens = 0
        output_tokens = 0
        result_json = {}

        try:
            if self.client:
                config = types.GenerateContentConfig(
                    temperature=0.2
                )
                res = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=config
                )
                raw_text = res.text.strip()
                if hasattr(res, "usage_metadata") and res.usage_metadata:
                    input_tokens = getattr(res.usage_metadata, "prompt_token_count", 0) or 0
                    output_tokens = getattr(res.usage_metadata, "candidates_token_count", 0) or 0

                # Pulizia JSON
                if raw_text.startswith("```"):
                    raw_text = raw_text.split("\n", 1)[1] if "\n" in raw_text else raw_text[3:]
                if raw_text.endswith("```"):
                    raw_text = raw_text[:-3]
                raw_text = raw_text.strip()
                result_json = json.loads(raw_text)
                
                # Normalizzazione robusta del campo areeInteresse per il radar chart
                if "areeInteresse" not in result_json:
                    for alt_key in ["areasInteresse", "aree_interesse", "aree", "aree_di_interesse", "interests"]:
                        if alt_key in result_json:
                            result_json["areeInteresse"] = result_json.pop(alt_key)
                            break

                # Se areeInteresse è ancora vuoto o non conforme, genera 6 aree graduate
                if not result_json.get("areeInteresse") or not isinstance(result_json.get("areeInteresse"), list) or len(result_json.get("areeInteresse")) < 3:
                    m1 = materie[0] if materie else "Scienze & Logica"
                    m2 = materie[1] if len(materie) > 1 else "Tecnologie Applicate"
                    a1 = aspirazioni[0] if aspirazioni else "Ingegneria & Design"
                    result_json["areeInteresse"] = [
                        {"nome": m1, "percentuale": 90},
                        {"nome": m2, "percentuale": 80},
                        {"nome": a1, "percentuale": 75},
                        {"nome": "Problem Solving", "percentuale": 70},
                        {"nome": "Innovazione Digitale", "percentuale": 60},
                        {"nome": "Ricerca & Sviluppo", "percentuale": 50}
                    ]

                # Allega KPI mirati
                corso = result_json.get("corsoConsigliato", "")
                cid = find_course_id_by_name(corso)
                if cid:
                    kpi = get_kpi(cid)
                    if kpi:
                        result_json["kpiData"] = kpi
                        result_json["courseKpiId"] = cid
        except Exception as e:
            result_json = {"error": str(e)}

        t3 = time.perf_counter()
        t4 = time.perf_counter()
        t5 = time.perf_counter()

        result_json["telemetry"] = {
            "t0": t0, "t1": t1, "t2": t2, "t3": t3, "t4": t4, "t5": t5,
            "t_network_pre_ms": round((t1 - t0) * 1000, 2),
            "t_retrieval_ms": round((t2 - t1) * 1000, 2),
            "t_llm_ms": round((t3 - t2) * 1000, 2),
            "t_post_ms": round((t4 - t3) * 1000, 2),
            "t_total_ms": round((t5 - t0) * 1000, 2),
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens
        }

        return result_json
