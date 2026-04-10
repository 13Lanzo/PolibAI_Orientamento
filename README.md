# 🎓 PolibAI - Assistente Navigazione e Orientamento (Angular + Flask)

Benvenuto nella repository del progetto **PolibAI**, il chatbot intelligente basato su architettura full-stack integrata. Questo software offre un chatbot avanzato per l'orientamento universitario e il recupero interattivo di raccomandazioni (Course Advisor), oltre alla navigazione su mappe interne.

L'architettura del sistema si divide in:
1. **Frontend:** Angular (Servito in locale sulla porta 4201)
2. **Backend:** Python + Flask (Servito in locale sulla porta 5000)
3. **AI Provider:** Google Gemini API (`gemini-3.1-flash-lite-preview`)
4. **Database Locale:** MySQL XAMPP (Per la gestione delle mappe fisiche del campus)

---

## 📋 1. Prerequisiti

Per eseguire questo progetto sul tuo ambiente locale necessiti dei seguenti strumenti:

- **[Node.js](https://nodejs.org/it/)** (LTS raccomandato) e `npm`
- **[Python](https://www.python.org/downloads/)** 3.9 o superiore
- **[XAMPP](https://www.apachefriends.org/it/index.html)** (se desideri utilizzare la logica delle mappe per il database `poliba_chatbot`)
- Una **Google Gemini API Key** valida acquisibile su Google AI Studio.

---

## ⚙️ 2. Installazione e Configurazione

### A. Preparare il Frontend (Angular)
1. Apri un terminale nella cartella root del progetto (`progetto_sw`).
2. Digita il comando per scaricare ed installare tutte le librerie grafiche e le logiche frontend:
```bash
npm install
```

### B. Preparare il Backend (Python/Flask)
1. Spostati nella cartella `backend`.
2. Assicurati di avere tutti i moduli principali installati tramine `pip`:
```bash
pip install flask flask-cors python-dotenv google-generativeai mysql-connector-python
```
*(Nota: in una revisione futura, `google-generativeai` sarà aggiornato alla nuova suite `google-genai`)*

3. Crea un file chiamato `.env` all'interno della cartella `backend/` e inserisci il seguente contenuto:
```env
GOOGLE_API_KEY="inserisci_qui_la_tua_api_key_reale"
```

### C. (Opzionale) Configurare il Database MySQL tramite XAMPP
Avvia il pannello di controllo XAMPP e accendi il modulo `MySQL`. 
Dovrai importare lo schema `poliba_chatbot` per utilizzare il sub-routing basato su database MySQL integrato sulle mappe dei laboratori.

---

## 🚀 3. Come Avviare il Progetto

Ci sono due modi per lanciare la suite. Il primo fa tutto automaticamente (raccomandato su Windows).

### METODO RAPIDO (Script su Windows)
Nella cartella root del progetto, troverai il file `start_all.bat`. Ti basterà fare doppio click su esso.
Lo script aprirà automaticamente due terminali:
- Uno dedicato all'avvio in background del server Python.
- Un altro dedicato all'avvio del server locale Angular.

### METODO MANUALE
Se ti trovi su macOS/Linux o preferisci avviare l'ispezione manuale:

**Terminale 1: Avviare il Backend Python**
```bash
cd backend
python chatbot.py
```
*\*Attendi che la console restituisca `TROVATO: models/gemini-3.1-flash-lite-preview` e `Running on http://127.0.0.1:5000`.*

**Terminale 2: Avviare l'App Web (Angular Frontend)**
```bash
# Usa il terminale puntato alla root progetto_sw
npm start
```

---

## 🌐 4. Utilizzo e Test
Se tutto è andato a buon fine, naviga dal tuo browser al seguente indirizzo per utilizzare subito PolibAI!

**👉 http://127.0.0.1:4201/**

Verrai accolto dall'interfaccia interattiva dell'assistente che ti guiderà alla scoperta dei piani Magistrali o dei Laboratori (e potrai visualizzare le famose **Infografiche Dinamiche** incluse staticamente nel frontend Angular interagendo col Bot!).
