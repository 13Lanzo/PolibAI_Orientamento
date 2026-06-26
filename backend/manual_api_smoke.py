"""Smoke test manuale per server Flask gia avviato.

Uso:
    python backend/manual_api_smoke.py

Non sostituisce i test automatici: serve solo per verificare rapidamente /chat e
/recommend quando il backend ha una chiave Gemini configurata.
"""

import json
import urllib.error
import urllib.request


BASE_URL = "http://127.0.0.1:5000"


def post_json(path, payload):
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        BASE_URL + path,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            body = response.read().decode("utf-8")
            print(path, response.status)
            print(body[:1000])
    except urllib.error.HTTPError as exc:
        print(path, exc.code)
        print(exc.read().decode("utf-8")[:1000])


if __name__ == "__main__":
    post_json("/chat", {"message": "Quali corsi di ingegneria informatica offre il Poliba?"})
    post_json(
        "/recommend",
        {
            "materie": ["matematica", "informatica"],
            "aspirazioni": ["sviluppatore software", "automazione"],
            "note": "Mi piacciono robotica e programmazione.",
        },
    )
