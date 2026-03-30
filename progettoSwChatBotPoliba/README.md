# Poliba Orientamento AI - Chatbot 🎓

Questo progetto è l'Assistente Virtuale Ufficiale per l'Orientamento Universitario del Politecnico di Bari. È progettato per aiutare i futuri studenti, interagendo in modo intelligente basandosi su documenti ufficiali, offrendo indicazioni di navigazione all'interno del campus e generando infografiche per i corsi di laurea!

L'architettura del progetto è suddivisa in due parti principali:
- **Frontend**: un'applicazione moderna sviluppata in Angular.
- **Backend**: un server Python basato su Flask, che si integra con l'API di Google Gemini per l'elaborazione del linguaggio naturale e con un DB MySQL per le informazioni sul campus.

---

## 🚀 Prerequisiti per l'installazione

Per eseguire correttamente questo progetto sul tuo computer, assicurati di avere installato:
1. **Node.js e npm** (per il frontend in Angular).
2. **Python 3.10+ e pip** (per il server backend).
3. **XAMPP / MySQL** (per il database delle mappe del campus).
4. Una **chiave API Google Gemini**, ottenibile tramite Google AI Studio.

---

## 🛠️ Configurazione e Avvio del Progetto

Segui questi due passaggi principali per avviare l'applicazione in locale. Assicurati di aprire **due terminali separati**, uno per il Backend e uno per il Frontend.

### 1. Avvio del Backend (Python / Flask)

Il backend gestisce l'intelligenza artificiale, le richeste sui corsi (suggerendo e servendo localmente infografiche statiche) e le interrogazioni al database.

1. Apri un terminale e spostati nella cartella root del progetto.
2. Assicurati che il server MySQL (es. tramite XAMPP) sia in esecuzione (database richiesto: `poliba_chatbot`).
3. Installa le dipendenze Python necessarie:
   ```bash
   pip install flask flask-cors google-generativeai mysql-connector-python python-dotenv
   ```
4. Crea un file `.env` nella cartella `backend/` e inserisci la tua API key di Gemini:
   ```env
   GOOGLE_API_KEY=la_tua_chiave_api_qui
   ```
5. Avvia il server backend:
   ```bash
   python backend/chatbot.py
   ```
   *Il server sarà in ascolto su `http://127.0.0.1:5000`*.

### 2. Avvio del Frontend (Angular)

Il frontend contiene l'interfaccia chat interattiva e dinamica.

1. Apri un secondo terminale, sempre nella cartella root del progetto.
2. Installa tutte le dipendenze Node:
   ```bash
   npm install
   ```
3. Avvia il server di sviluppo Angular:
   ```bash
   npm start
   ```
   *Oppure usa `ng serve` se hai Angular CLI installato globalmente.*
4. Visita [http://localhost:4201](http://localhost:4201) (o la porta specificata nel tuo terminale) sul tuo browser!

---

## ✨ Funzionalità Principali

* **Retrieval-Augmented Generation (RAG)**: Il bot basa le sue risposte sui bandi e sulle guide dello studente ufficiali.
* **Mappe Dinamiche**: Piena integrazione basata su DB per istruire lo studente nell'orientamento fisico all'interno dei plessi del campus (via Orabona, ecc.).
* **Infografiche Dinamiche**: Ricerca i corsi di Ingegneria (Medicale, Informatica, Edile, ecc.) per far apparire le opzioni con l'Infografica correlata istantaneamente generata/caricata in chat.
* **Calcolo Tasse Context-Aware**.
