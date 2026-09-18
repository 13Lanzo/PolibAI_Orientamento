import os
import sys
import time
import json
import concurrent.futures
from typing import Dict, Any, List

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "backend"))
from optimized_engine import OptimizedPolibAIEngine
from evaluate_metrics import calc_distribution_percentiles

def run_concurrency_test():
    print("=== AVVIO CONCURRENCY & LOAD TESTING (1, 2, 5, 10 WORKERS) ===")
    engine = OptimizedPolibAIEngine()

    test_queries = [
        ("user_A", "Quali sono i requisiti per il bando Erasmus e quanti CFU servono?"),
        ("user_B", "Qual è la no-tax area per le tasse universitarie del Politecnico?"),
        ("user_C", "Qual è la retribuzione media a un anno per Ingegneria Gestionale?"),
        ("user_D", "Come arrivo alla biblioteca PoliLibrary da Via Orabona?"),
        ("user_E", "Quali sono le materie caratterizzanti di Ingegneria Informatica?")
    ]

    concurrency_levels = [1, 2, 5, 10]
    concurrency_summary = []

    for c in concurrency_levels:
        print(f"\n>> Test con {c} utenti concorrenti...")
        start_time = time.perf_counter()
        latencies = []
        tokens_input = []
        tokens_output = []
        errors = 0
        completed = 0
        leakage_detected = 0

        # Eseguiamo 20 richieste complessive con quel livello di concorrenza
        total_requests = 20
        tasks = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=c) as executor:
            for req_idx in range(total_requests):
                user_id, q_text = test_queries[req_idx % len(test_queries)]
                # Unique session id per isolamento
                session_id = f"worker_{c}_user_{req_idx}"
                fut = executor.submit(engine.process_chat_optimized, q_text, session_id, 5)
                tasks.append((fut, user_id, q_text, session_id))

            for fut, uid, q_text, sid in tasks:
                try:
                    res = fut.result()
                    tel = res.get("telemetry", {})
                    lat = tel.get("t_total_ms", 0.0)
                    in_t = tel.get("input_tokens", 0)
                    out_t = tel.get("output_tokens", 0)
                    latencies.append(lat)
                    tokens_input.append(in_t)
                    tokens_output.append(out_t)
                    completed += 1

                    # Verifica cross-user leakage: controlla che la sessione contenga solo i messaggi dell'utente
                    sess = engine.session_manager.get_session(sid)
                    user_msgs = [m["content"] for m in sess["history"] if m["role"] == "user"]
                    if len(user_msgs) != 1 or user_msgs[0] != q_text:
                        leakage_detected += 1
                except Exception as e:
                    errors += 1

        duration_sec = time.perf_counter() - start_time
        throughput_rpm = round((completed / max(0.01, duration_sec)) * 60, 2)
        total_tpm = round((sum(tokens_input) / max(0.01, duration_sec)) * 60, 2)
        dist = calc_distribution_percentiles(latencies)

        row = {
            "concurrency": c,
            "total_requests": total_requests,
            "completed": completed,
            "errors": errors,
            "error_rate_percent": round((errors / total_requests) * 100, 2),
            "duration_sec": round(duration_sec, 2),
            "throughput_rpm": throughput_rpm,
            "total_tpm": total_tpm,
            "p50_ms": dist["p50"],
            "p95_ms": dist["p95"],
            "p99_ms": dist["p99"],
            "avg_latency_ms": dist["mean"],
            "leakage_rate_percent": round((leakage_detected / max(1, completed)) * 100, 2)
        }
        concurrency_summary.append(row)
        print(f"   Completate: {completed}/{total_requests} in {row['duration_sec']}s | Throughput: {throughput_rpm} req/min | p50: {dist['p50']}ms, p95: {dist['p95']}ms | Leakage: {row['leakage_rate_percent']}%")

    out_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "concurrency_results.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(concurrency_summary, f, indent=2)

    print(f"\n[LOAD TESTING COMPLETATO] Risultati salvati in {out_file}")
    return concurrency_summary

if __name__ == "__main__":
    run_concurrency_test()
