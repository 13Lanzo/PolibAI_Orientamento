# Poliba Orientamento AI - Chatbot 🎓

Assistente Virtuale Ufficiale per l'Orientamento Universitario del Politecnico di Bari.  
Interagisce in modo intelligente basandosi su documenti ufficiali, offre indicazioni di navigazione nel campus e mostra infografiche statiche per i corsi di laurea.

## Architettura

| Layer | Tecnologia | Porta |
|-------|-----------|-------|
| **Frontend** | React 19 + Vite + TypeScript | `4201` |
| **Backend** | Python Flask + Google Gemini API | `5000` |
| **Database** | MySQL (XAMPP) | `3306` |

---

## 🚀 Prerequisiti

1. **Node.js 18+** e **npm**
2. **Python 3.10+** e **pip**
3. **XAMPP / MySQL** (per il database `poliba_chatbot` con le mappe campus)
4. Una **chiave API Google Gemini** da [Google AI Studio](https://aistudio.google.com/)

---

## 🛠️ Setup e Avvio

### 1. Backend (Flask)

```bash
# Installa le dipendenze Python
pip install flask flask-cors google-generativeai mysql-connector-python python-dotenv

# Crea il file .env nella cartella backend/
echo GOOGLE_API_KEY=la_tua_chiave > backend/.env

# Avvia il server
python backend/chatbot.py
```
Il server sarà in ascolto su `http://127.0.0.1:5000`.

### 2. Frontend (React + Vite)

```bash
# Installa le dipendenze Node
npm install

# Avvia il dev server
npm start
```
L'interfaccia sarà disponibile su [http://127.0.0.1:4201](http://127.0.0.1:4201).

---

## ✨ Funzionalità

- **RAG (Retrieval-Augmented Generation)**: risposte basate su Guida dello Studente, regolamento tasse e bando Erasmus
- **Mappe Campus**: navigazione interattiva con scelta dell'ingresso e mappa dinamica da MySQL
- **Infografiche Statiche**: bottoni contestuali per visualizzare infografiche pre-caricate dei corsi di laurea (L7, L8, L9)
- **Markdown Rendering**: risposte formattate con grassetto, elenchi e emoji

---

## 📁 Struttura del Progetto

```
├── backend/
│   ├── chatbot.py          # Server Flask + logica AI + routing infografiche
│   ├── polibaDB.py         # Utility MySQL
│   ├── knowledge/          # PDF della conoscenza (guide, bandi, regolamenti)
│   └── .env                # API key (non versionato)
├── public/
│   ├── assets/
│   │   ├── images/maps/    # Mappe campus
│   │   └── infografiche/   # Infografiche statiche dei corsi
│   └── favicon.ico
├── src/
│   ├── api/chatService.ts  # Client HTTP per il backend
│   ├── components/
│   │   └── Chatbot/
│   │       ├── Chatbot.tsx  # Componente principale React
│   │       └── Chatbot.css  # Stili del chatbot
│   ├── App.tsx
│   ├── main.tsx
│   └── index.css
├── vite.config.ts
├── tsconfig.json
└── package.json
```

---

## 📝 Note

- Le infografiche sono gestite lato backend (`chatbot.py`): il server analizza la risposta di Gemini e inietta automaticamente i bottoni "Mostra Infografica" quando rileva un corso di laurea nella risposta.
- Il frontend è completamente data-driven: non contiene alcuna logica hardcoded per i corsi.
