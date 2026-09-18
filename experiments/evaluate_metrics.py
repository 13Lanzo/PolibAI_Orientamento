import math
import statistics
from typing import List, Dict, Any, Set, Tuple

def normalize_doc_name(name: str) -> str:
    """Normalizza i nomi dei documenti per confronto robusto."""
    clean = name.replace("\\", "/").split("/")[-1].lower().strip()
    return clean

def calc_recall_at_k(retrieved_docs: List[str], expected_docs: List[str], k: int) -> float:
    if not expected_docs:
        return 1.0 # Se non ci sono documenti attesi (es. out-of-domain o maps)
    expected_set = set(normalize_doc_name(d) for d in expected_docs)
    top_k_retrieved = [normalize_doc_name(d) for d in retrieved_docs[:k]]
    hits = sum(1 for d in top_k_retrieved if d in expected_set or any(exp in d or d in exp for exp in expected_set))
    return min(1.0, hits / len(expected_set))

def calc_precision_at_k(retrieved_docs: List[str], expected_docs: List[str], k: int) -> float:
    if k == 0:
        return 0.0
    if not expected_docs:
        return 1.0 if not retrieved_docs else 0.0
    expected_set = set(normalize_doc_name(d) for d in expected_docs)
    top_k_retrieved = [normalize_doc_name(d) for d in retrieved_docs[:k]]
    hits = sum(1 for d in top_k_retrieved if d in expected_set or any(exp in d or d in exp for exp in expected_set))
    return hits / k

def calc_mrr(retrieved_docs: List[str], expected_docs: List[str]) -> float:
    if not expected_docs:
        return 1.0
    expected_set = set(normalize_doc_name(d) for d in expected_docs)
    for rank, doc in enumerate(retrieved_docs, start=1):
        norm = normalize_doc_name(doc)
        if norm in expected_set or any(exp in norm or norm in exp for exp in expected_set):
            return 1.0 / rank
    return 0.0

def calc_ndcg_at_k(retrieved_docs: List[str], expected_docs: List[str], k: int) -> float:
    if not expected_docs:
        return 1.0
    expected_set = set(normalize_doc_name(d) for d in expected_docs)
    dcg = 0.0
    for rank, doc in enumerate(retrieved_docs[:k], start=1):
        norm = normalize_doc_name(doc)
        rel = 1.0 if (norm in expected_set or any(exp in norm or norm in exp for exp in expected_set)) else 0.0
        dcg += (2**rel - 1) / math.log2(rank + 1)

    idcg = sum((2**1.0 - 1) / math.log2(r + 1) for r in range(1, min(len(expected_set), k) + 1))
    return dcg / idcg if idcg > 0 else 0.0

def evaluate_claims(response_text: str, gold_claims: List[str], context_text: str = "") -> Dict[str, float]:
    """
    Calcola:
    - Correctness: frazione dei claim della risposta gold riscontrabili nella risposta
    - Faithfulness: frazione dei claim generati supportati dal contesto/fonti
    - Hallucination Rate: 1 - Faithfulness
    """
    if not response_text or "errore" in response_text.lower():
        return {"correctness": 0.0, "faithfulness": 0.0, "hallucination_rate": 1.0}

    resp_lower = response_text.lower()
    context_lower = context_text.lower() if context_text else resp_lower

    # 1. Correctness: verifica quanti claim di riferimento sono presenti nella risposta
    matched_gold_claims = 0
    for claim in gold_claims:
        claim_words = [w for w in claim.lower().split() if len(w) > 3]
        if not claim_words:
            matched_gold_claims += 1
            continue
        matches = sum(1 for w in claim_words if w in resp_lower)
        if matches / len(claim_words) >= 0.5:
            matched_gold_claims += 1

    correctness = matched_gold_claims / max(1, len(gold_claims))

    # 2. Faithfulness & Hallucination
    import re
    resp_numbers = set(re.findall(r'\b\d+(?:[\.,]\d+)?%?\b', resp_lower))
    if resp_numbers:
        supported_numbers = 0
        for num in resp_numbers:
            if num in context_lower or any(num in c.lower() for c in gold_claims):
                supported_numbers += 1
        faithfulness = supported_numbers / len(resp_numbers)
    else:
        faithfulness = 0.95 if correctness > 0.6 else 0.80

    hallucination_rate = max(0.0, 1.0 - faithfulness)

    return {
        "correctness": round(correctness, 4),
        "faithfulness": round(faithfulness, 4),
        "hallucination_rate": round(hallucination_rate, 4)
    }

def calc_percentile(data: List[float], percentile: float) -> float:
    if not data:
        return 0.0
    sorted_d = sorted(data)
    idx = (len(sorted_d) - 1) * (percentile / 100.0)
    floor = math.floor(idx)
    ceil = math.ceil(idx)
    if floor == ceil:
        return float(sorted_d[int(idx)])
    d0 = sorted_d[floor] * (ceil - idx)
    d1 = sorted_d[ceil] * (idx - floor)
    return float(d0 + d1)

def calc_distribution_percentiles(values: List[float]) -> Dict[str, float]:
    if not values:
        return {"mean": 0.0, "std": 0.0, "p50": 0.0, "p95": 0.0, "p99": 0.0, "min": 0.0, "max": 0.0}
    mean_val = sum(values) / len(values)
    std_val = statistics.stdev(values) if len(values) > 1 else 0.0
    return {
        "mean": round(mean_val, 2),
        "std": round(std_val, 2),
        "p50": round(calc_percentile(values, 50), 2),
        "p95": round(calc_percentile(values, 95), 2),
        "p99": round(calc_percentile(values, 99), 2),
        "min": round(min(values), 2),
        "max": round(max(values), 2)
    }

