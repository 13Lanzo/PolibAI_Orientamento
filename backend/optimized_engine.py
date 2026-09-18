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
# 4. OPTIMIZED ENGINE WITH INTENT ROUTER & TELEMETRY
# =============================================================================

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
        if any(w in msg_lower for w in ["dov'è", "dove si trova", "come arrivo", "come raggiungo", "posizione biblioteca", "aula", "edificio"]):
            return "MAPS_ROUTING"
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

        retrieved_chunks = []
        context_text = ""
        
        # A. Intent Routing
        if intent == "MAPS_ROUTING":
            # Risposta deterministica veloce o query mirata
            t2 = time.perf_counter()
            dest = "poliLibrary" if "biblioteca" in message.lower() else ("LabDDV" if "lab" in message.lower() else "Edificio Principale")
            t3 = time.perf_counter()
            response_text = f"Per raggiungere {dest}, ti consiglio di accedere dall'ingresso principale di Via Orabona. Puoi selezionare l'ingresso per visualizzare la mappa topografica."
            t4 = time.perf_counter()
            t5 = time.perf_counter()
            
            return {
                "response": response_text,
                "type": "options",
                "options": [
                    {"label": "📍 Via Orabona (Principale)", "value": "Orabona1"},
                    {"label": "📍 Via Re David", "value": "reDavid"}
                ],
                "telemetry": {
                    "t0": t0, "t1": t1, "t2": t2, "t3": t3, "t4": t4, "t5": t5,
                    "t_network_pre_ms": round((t1 - t0) * 1000, 2),
                    "t_retrieval_ms": round((t2 - t1) * 1000, 2),
                    "t_llm_ms": round((t3 - t2) * 1000, 2),
                    "t_post_ms": round((t4 - t3) * 1000, 2),
                    "t_total_ms": round((t5 - t0) * 1000, 2),
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "total_tokens": 0,
                    "intent": intent,
                    "top_k": 0,
                    "retrieved_docs": []
                }
            }

        # B. Selective Retrieval top-k
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
            "Sei PolibAI PRO, assistente ufficiale per l'orientamento del Politecnico di Bari.\n"
            "Basa la risposta rigorosamente sui seguenti estratti documentali ufficiali pertinenti.\n"
            "Se l'informazione non è presente negli estratti o nei KPI allegati, dichiaralo con chiarezza.\n"
            f"\n[ESTRATTI DOCUMENTALI SELEZIONATI TOP-{top_k}]:\n{context_text}\n{kpi_snippet}"
        )

        prompt = message
        input_tokens = 0
        output_tokens = 0
        response_text = ""

        try:
            if self.client:
                config = types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.2
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
            f"Materie: {', '.join(materie) if materie else 'non indicate'}\n"
            f"Aspirazioni: {', '.join(aspirazioni) if aspirazioni else 'non indicate'}\n"
            f"Note: {note}\n"
            "Raccomanda il corso di laurea più adatto secondo le regole Poliba (distingui accuratamente tra Triennale e Magistrale)."
        )

        from chatbot import istruzioni_advisor
        prompt = f"{istruzioni_advisor}\n\n[CONTESTO SELETTIVO RIDOTTO]:\n{kb_context}\n\n{user_message}"

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
