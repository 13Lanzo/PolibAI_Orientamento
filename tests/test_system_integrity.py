import os
import sys
import json

# Aggiungi backend al sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

from chatbot import app
from kpi_data import COURSE_KPI

def run_tests():
    print("==================================================")
    print("TEST DI INTEGRITÀ E VALIDAZIONE DEL SISTEMA POLIBAI")
    print("==================================================")
    
    client = app.test_client()

    # 1. Test Endpoint /analysis
    print("\n1. Test Endpoint /analysis (Ingegneria Informatica e dell'Automazione)...")
    res = client.get('/analysis?course_id=IIA')
    assert res.status_code == 200, f"Status code errato: {res.status_code}"
    data = res.get_json()
    assert data.get("course_id") == "IIA"
    assert "almalaurea" in data
    assert "opis" in data
    print("   -> OK! KPI recuperati correttamente per IIA.")

    # 2. Test Endpoint /kpis
    print("\n2. Test Endpoint /kpis (Lista completa corsi)...")
    res = client.get('/kpis')
    assert res.status_code == 200
    data = res.get_json()
    assert "courses" in data
    assert len(data["courses"]) >= 10
    print(f"   -> OK! Restituiti {len(data['courses'])} corsi con KPI.")

    # 3. Test Endpoint /chat con domanda accademica
    print("\n3. Test Endpoint /chat (Query accademica)...")
    payload = {
        "message": "Quali corsi triennali offre il dipartimento DEI?",
        "sessionId": "test_verification_session_1"
    }
    res = client.post('/chat', json=payload)
    assert res.status_code == 200, f"Errore /chat: {res.status_code} - {res.data}"
    chat_data = res.get_json()
    assert "response" in chat_data
    assert len(chat_data["response"]) > 20
    print(f"   -> OK! Risposta ricevuta (lunghezza: {len(chat_data['response'])} car).")
    print(f"   -> Estratto risposta: {chat_data['response'][:120]}...")

    # 4. Test Endpoint /chat con domanda su localizzazione campus (ex-modulo mappe)
    print("\n4. Test Endpoint /chat (Query localizzazione campus, ora gestita via RAG/LLM)...")
    payload = {
        "message": "Dove si trova la biblioteca centrale del Politecnico di Bari?",
        "sessionId": "test_verification_session_2"
    }
    res = client.post('/chat', json=payload)
    assert res.status_code == 200, f"Errore /chat: {res.status_code} - {res.data}"
    campus_data = res.get_json()
    assert "response" in campus_data
    # Assicuriamoci che non restituisca bottoni MySQL rotti, ma una risposta testuale fluida
    assert campus_data.get("type") == "text"
    print(f"   -> OK! Nessun blocco MySQL, risposta text generata:")
    print(f"   -> {campus_data['response'][:150]}...")

    # 5. Test Endpoint /recommend (Course Advisor)
    print("\n5. Test Endpoint /recommend (Profilo studente per radar chart)...")
    rec_payload = {
        "materie": ["Matematica", "Informatica", "Fisica"],
        "aspirazioni": ["Sviluppare software", "Intelligenza Artificiale"],
        "note": "Cerco una laurea triennale dinamica con molti laboratori"
    }
    res = client.post('/recommend', json=rec_payload)
    assert res.status_code == 200, f"Errore /recommend: {res.status_code} - {res.data}"
    rec_data = res.get_json()
    assert "corsoConsigliato" in rec_data
    assert "areeInteresse" in rec_data
    assert len(rec_data["areeInteresse"]) == 6, f"areeInteresse deve avere 6 elementi, trovati {len(rec_data['areeInteresse'])}"
    print(f"   -> OK! Corso consigliato: {rec_data['corsoConsigliato']}")
    print(f"   -> 6 Aree radar chart verificate: {[a['nome'] for a in rec_data['areeInteresse']]}")

    print("\n==================================================")
    print("TUTTI I TEST DI VALIDAZIONE SONO PASSATI CON SUCCESSO! (5/5)")
    print("==================================================")

if __name__ == "__main__":
    run_tests()
