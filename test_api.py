import urllib.request
import json
import time

def test_endpoint(url, payload):
    start = time.time()
    req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'}, method='POST')
    try:
        with urllib.request.urlopen(req) as response:
            res_body = response.read().decode('utf-8')
            elapsed = time.time() - start
            print(f"[OK] [{elapsed:.2f}s]: {url}")
            print(f"Risposta: {res_body[:300]}...")
    except Exception as e:
        elapsed = time.time() - start
        print(f"[ERROR] [{elapsed:.2f}s]: {url} -> {e}")

print("=== TEST CHATBOT ===")
test_endpoint('http://127.0.0.1:5000/chat', {'message': 'Come funzionano i test di ammissione al Poliba?'})

print("\n=== TEST COURSE ADVISOR ===")
test_endpoint('http://127.0.0.1:5000/recommend', {'materie': ['Matematica', 'Fisica'], 'aspirazioni': ['Sviluppo Software', 'Intelligenza Artificiale']})
