# =============================================================================
# KPI DATA STORE — Dati estratti dai report OPIS e AlmaLaurea
# =============================================================================
# Questo modulo contiene i KPI strutturati per ogni corso di laurea.
# I dati provengono dai file .md nella cartella knowledge/.
#
# FONTE ALMALAUREA: "Analisi Occupazionale e Soddisfazione Laureati
#   Politecnico di Bari - Rapporto 2025"
# FONTE OPIS: Rapporti OPIS 2024 per singolo corso (cartella Recensioni Studenti)
#
# MEDIA DI ATENEO (riferimento per il giudizio comparativo):
#   - Triennali: 80.5% occupazione a 1 anno (chi non prosegue)
#   - Magistrali: ~91% occupazione a 1 anno
#   - Crescita salariale media magistrale a 5 anni: +25.6%
# =============================================================================

MEDIA_ATENEO_OCCUPAZIONE_TRIENNALE = 80.5
MEDIA_ATENEO_OCCUPAZIONE_MAGISTRALE = 91.0

def _calcola_giudizio(tasso_occupazione, livello="triennale"):
    """Calcola se il tasso di occupazione è superiore o inferiore alla media di Ateneo."""
    media = MEDIA_ATENEO_OCCUPAZIONE_TRIENNALE if livello == "triennale" else MEDIA_ATENEO_OCCUPAZIONE_MAGISTRALE
    delta = round(tasso_occupazione - media, 1)
    return {
        "occupazione_vs_media": "superiore" if delta > 0 else ("nella media" if delta == 0 else "inferiore"),
        "delta_occupazione": delta
    }


# =============================================================================
# DIZIONARIO KPI PER CORSO
# =============================================================================
# Chiavi: stessi ID usati nelle infografiche frontend (IIA, IMED, IGEST, ecc.)
# Dati reali dal Rapporto AlmaLaurea 2025 per il Poliba.
# =============================================================================

COURSE_KPI = {

    # ─── INGEGNERIA INFORMATICA E DELL'AUTOMAZIONE (L-8) ────────────────
    "IIA": {
        "nome": "Ingegneria Informatica e dell'Automazione",
        "classe": "L-8",
        "dipartimento": "DEI",
        "anno": "2024/2025",
        "livello": "triennale",
        "source_almalaurea": "Analisi Occupazionale e Soddisfazione Laureati Politecnico di Bari - Rapporto 2025",
        "almalaurea": {
            "tasso_occupazione_1_anno": 97.5,
            "retribuzione_netta_media": 1350,
            "soddisfazione_corso": 93.3,
            "tasso_occupazione_3_anni": None,
            "retribuzione_netta_media_3_anni": None,
            "tasso_occupazione_5_anni": None,
            "retribuzione_netta_media_5_anni": None,
            "impatto_studi_titolo": "Proseguimento con Laurea Magistrale",
            "impatto_studi_valore": "85.1%",
            "impatto_studi_descrizione": "L'85.1% prosegue con la magistrale. Retribuzione triennale: 1.350€, +150€ vs media Ateneo."
        },
        "giudizio_comparativo": _calcola_giudizio(97.5, "triennale"),
        "recensioni": [{"parametro": "Il carico di studio dell'insegnamento è proporzionato ai crediti assegnati?", "valore": "100%"}, {"parametro": "Le modalità di esame sono state definite in modo chiaro?", "valore": "100%"}],
        "note": "Dati Dashboard AlmaLaurea 2024. 97.5% occupati su forze lavoro, 1.350€/mese."
    },

    # ─── INGEGNERIA DEI SISTEMI MEDICALI (L-8) ──────────────────────────
    "IMED": {
        "nome": "Ingegneria dei Sistemi Medicali",
        "classe": "L-8",
        "dipartimento": "DEI",
        "anno": "2024/2025",
        "livello": "triennale",
        "source_almalaurea": "Analisi Occupazionale e Soddisfazione Laureati Politecnico di Bari - Rapporto 2025",
        "almalaurea": {
            "tasso_occupazione_1_anno": 78.6,
            "retribuzione_netta_media": 1314,
            "soddisfazione_corso": 97.5,
            "tasso_occupazione_3_anni": None,
            "retribuzione_netta_media_3_anni": None,
            "tasso_occupazione_5_anni": None,
            "retribuzione_netta_media_5_anni": None,
            "impatto_studi_titolo": "Proseguimento con Magistrale LM-21",
            "impatto_studi_valore": "93.1%",
            "impatto_studi_descrizione": "Il 93.1% prosegue con la magistrale. Soddisfazione globale 97.5%, la più alta tra le triennali DEI."
        },
        "giudizio_comparativo": _calcola_giudizio(78.6, "triennale"),
        "recensioni": [{"parametro": "È interessato/a agli argomenti trattati nell'insegnamento?", "valore": "87.27%"}, {"parametro": "Le conoscenze preliminari possedute sono risultate sufficienti per la comprensione degli argomenti previsti nel programma d'esame?", "valore": "85.37%"}],
        "note": "Dati Dashboard AlmaLaurea 2024. 78.6% occupati su forze lavoro, 1.314€/mese, 97.5% soddisfatti."
    },

    # ─── INGEGNERIA MECCANICA (L-9) ─────────────────────────────────────
    "IMEC": {
        "nome": "Ingegneria Meccanica",
        "classe": "L-9",
        "dipartimento": "DMMM",
        "anno": "2024/2025",
        "livello": "triennale",
        "source_almalaurea": "Analisi Occupazionale e Soddisfazione Laureati Politecnico di Bari - Rapporto 2025",
        "almalaurea": {
            "tasso_occupazione_1_anno": 88.9,
            "retribuzione_netta_media": 1064,
            "soddisfazione_corso": 96.3,
            "tasso_occupazione_3_anni": None,
            "retribuzione_netta_media_3_anni": None,
            "tasso_occupazione_5_anni": None,
            "retribuzione_netta_media_5_anni": None,
            "impatto_studi_titolo": "Proseguimento con Magistrale Meccanica",
            "impatto_studi_valore": "91.5%",
            "impatto_studi_descrizione": "Il 91.5% prosegue con la magistrale. Uso elevato competenze: 50%, superiore alla media Ateneo (43%)."
        },
        "giudizio_comparativo": _calcola_giudizio(88.9, "triennale"),
        "recensioni": [{"parametro": "Ritiene che contenuti e metodi didattici del corso utilizzati dal docente siano adeguati alla modalità di erogazione della didattica a distanza?", "valore": "100%"}, {"parametro": "Si ritiene complessivamente soddisfatto dell'organizzazione del servizio di erogazione on-line della didattica?", "valore": "100%"}],
        "note": "Dati Dashboard AlmaLaurea 2024. 88.9% occupati su forze lavoro, 1.064€/mese, soddisfazione 96.3%."
    },

    # ─── INGEGNERIA GESTIONALE (L-9) ────────────────────────────────────
    "IGEST": {
        "nome": "Ingegneria Gestionale",
        "classe": "L-9",
        "dipartimento": "DMMM",
        "anno": "2024/2025",
        "livello": "triennale",
        "source_almalaurea": "Analisi Occupazionale e Soddisfazione Laureati Politecnico di Bari - Rapporto 2025",
        "almalaurea": {
            "tasso_occupazione_1_anno": 82.8,
            "retribuzione_netta_media": 1054,
            "soddisfazione_corso": 98.1,
            "tasso_occupazione_3_anni": None,
            "retribuzione_netta_media_3_anni": None,
            "tasso_occupazione_5_anni": None,
            "retribuzione_netta_media_5_anni": None,
            "impatto_studi_titolo": "Proseguimento con Magistrale Gestionale",
            "impatto_studi_valore": "91.9%",
            "impatto_studi_descrizione": "Il 91.9% prosegue con la magistrale. Soddisfazione globale 98.1%, tra le più alte del Poliba."
        },
        "giudizio_comparativo": _calcola_giudizio(82.8, "triennale"),
        "recensioni": [{"parametro": "I contenuti digitali resi disponibili in modalità asincrona sono risultati utili all'apprendimento della materia?", "valore": "84.25%"}, {"parametro": "Il materiale didattico (indicato e disponibile) è adeguato per lo studio della materia?", "valore": "79.21%"}],
        "note": "Dati Dashboard AlmaLaurea 2024. 82.8% occupati su forze lavoro, 1.054€/mese, soddisfazione 98.1%."
    },

    # ─── INGEGNERIA ELETTRONICA E TECNOLOGIE INTERNET (L-8) ─────────────
    "IETI": {
        "nome": "Ingegneria Elettronica e Tecnologie Internet",
        "classe": "L-8",
        "dipartimento": "DEI",
        "anno": "2024/2025",
        "livello": "triennale",
        "source_almalaurea": "Analisi Occupazionale e Soddisfazione Laureati Politecnico di Bari - Rapporto 2025",
        "almalaurea": {
            "tasso_occupazione_1_anno": 50.0,
            "retribuzione_netta_media": 1876,
            "soddisfazione_corso": 75.9,
            "tasso_occupazione_3_anni": None,
            "retribuzione_netta_media_3_anni": None,
            "tasso_occupazione_5_anni": None,
            "retribuzione_netta_media_5_anni": None,
            "impatto_studi_titolo": "Proseguimento con Magistrale Electronics",
            "impatto_studi_valore": "92.1%",
            "impatto_studi_descrizione": "Il 92.1% prosegue con la magistrale. Retribuzione triennale record: 1.876€, la più alta tra le triennali."
        },
        "giudizio_comparativo": _calcola_giudizio(50.0, "triennale"),
        "recensioni": [{"parametro": "Le modalità di esame sono state definite in modo chiaro?", "valore": "Positivo"}, {"parametro": "È interessato/a agli argomenti trattati nell'insegnamento?", "valore": "17.6%"}],
        "note": "Dati Dashboard AlmaLaurea 2024. 50% occupati su forze lavoro (campione ridotto), 1.876€/mese."
    },

    # ─── INGEGNERIA DEI SISTEMI AEROSPAZIALI (L-9) ──────────────────────
    "IAERO": {
        "nome": "Ingegneria dei Sistemi Aerospaziali",
        "classe": "L-9",
        "dipartimento": "DMMM",
        "anno": "2024/2025",
        "livello": "triennale",
        "source_almalaurea": "Analisi Occupazionale e Soddisfazione Laureati Politecnico di Bari - Rapporto 2025",
        "almalaurea": {
            "tasso_occupazione_1_anno": 100.0,
            "retribuzione_netta_media": 1627,
            "soddisfazione_corso": 100.0,
            "tasso_occupazione_3_anni": None,
            "retribuzione_netta_media_3_anni": None,
            "tasso_occupazione_5_anni": None,
            "retribuzione_netta_media_5_anni": None,
            "impatto_studi_titolo": "Proseguimento con Magistrale Aerospaziale",
            "impatto_studi_valore": "73.7%",
            "impatto_studi_descrizione": "100% soddisfazione globale, 100% occupati su forze lavoro, retribuzione 1.627€ (+422€ vs Ateneo)."
        },
        "giudizio_comparativo": _calcola_giudizio(100.0, "triennale"),
        "recensioni": [{"parametro": "Le modalità di esame sono state definite in modo chiaro?", "valore": "Positivo"}, {"parametro": "Gli orari di svolgimento di lezioni, esercitazioni e altre eventuali attività sono rispettati?", "valore": "Positivo"}],
        "note": "Dati Dashboard AlmaLaurea 2024. 100% occupati su forze lavoro, 1.627€/mese, 100% soddisfatti."
    },

    # ─── INGEGNERIA CIVILE E AMBIENTALE (L-7) ───────────────────────────
    "ICIVAMB": {
        "nome": "Ingegneria Civile e Ambientale",
        "classe": "L-7",
        "dipartimento": "DICATECh",
        "anno": "2024/2025",
        "livello": "triennale",
        "source_almalaurea": "Analisi Occupazionale e Soddisfazione Laureati Politecnico di Bari - Rapporto 2025",
        "almalaurea": {
            "tasso_occupazione_1_anno": 75.0,
            "retribuzione_netta_media": 1459,
            "soddisfazione_corso": 100.0,
            "tasso_occupazione_3_anni": None,
            "retribuzione_netta_media_3_anni": None,
            "tasso_occupazione_5_anni": None,
            "retribuzione_netta_media_5_anni": None,
            "impatto_studi_titolo": "Proseguimento con Magistrale Civile",
            "impatto_studi_valore": "94.1%",
            "impatto_studi_descrizione": "Il 94.1% prosegue con la magistrale. 100% soddisfazione globale, retribuzione 1.459€."
        },
        "giudizio_comparativo": _calcola_giudizio(75.0, "triennale"),
        "recensioni": [{"parametro": "Il docente è reperibile per chiarimenti e spiegazioni?", "valore": "37.04%"}, {"parametro": "Le modalità di esame sono state definite in modo chiaro?", "valore": "22.03%"}],
        "note": "Dati Dashboard AlmaLaurea 2024. 75% occupati su forze lavoro, 1.459€/mese, 100% soddisfatti."
    },

    # ─── INGEGNERIA ELETTRICA (L-9) ─────────────────────────────────────
    "IELE": {
        "nome": "Ingegneria dell'Energia Elettrica",
        "classe": "L-9",
        "dipartimento": "DEI",
        "anno": "2024/2025",
        "livello": "triennale",
        "source_almalaurea": "Analisi Occupazionale e Soddisfazione Laureati Politecnico di Bari - Rapporto 2025",
        "almalaurea": {
            "tasso_occupazione_1_anno": 100.0,
            "retribuzione_netta_media": 1192,
            "soddisfazione_corso": 92.0,
            "tasso_occupazione_3_anni": None,
            "retribuzione_netta_media_3_anni": None,
            "tasso_occupazione_5_anni": None,
            "retribuzione_netta_media_5_anni": None,
            "impatto_studi_titolo": "Proseguimento con Magistrale Elettrica/Energy",
            "impatto_studi_valore": "88.9%",
            "impatto_studi_descrizione": "100% occupati su forze lavoro. 70% uso elevato competenze, top Ateneo. 100% rapporti docenti positivi."
        },
        "giudizio_comparativo": _calcola_giudizio(100.0, "triennale"),
        "recensioni": [{"parametro": "Il docente è reperibile per chiarimenti e spiegazioni?", "valore": "Positivo"}],
        "note": "Dati Dashboard AlmaLaurea 2024. 100% occupati su forze lavoro, 1.192€/mese, 100% rapporti docenti."
    },

    # ─── INGEGNERIA EDILE (L-23) ────────────────────────────────────────
    "IEDILE": {
        "nome": "Ingegneria Edile",
        "classe": "L-23",
        "dipartimento": "DICATECh",
        "anno": "2024/2025",
        "livello": "triennale",
        "source_almalaurea": "Analisi Occupazionale e Soddisfazione Laureati Politecnico di Bari - Rapporto 2025",
        "almalaurea": {
            "tasso_occupazione_1_anno": 83.3,
            "retribuzione_netta_media": 1176,
            "soddisfazione_corso": 96.9,
            "tasso_occupazione_3_anni": None,
            "retribuzione_netta_media_3_anni": None,
            "tasso_occupazione_5_anni": None,
            "retribuzione_netta_media_5_anni": None,
            "impatto_studi_titolo": "Proseguimento con Magistrale Edile",
            "impatto_studi_valore": "90.9%",
            "impatto_studi_descrizione": "Il 90.9% prosegue con la magistrale. 60% uso elevato competenze (top Ateneo), soddisfazione lavoro 8/10."
        },
        "giudizio_comparativo": _calcola_giudizio(83.3, "triennale"),
        "recensioni": [{"parametro": "I contenuti digitali resi disponibili in modalità asincrona sono risultati utili all'apprendimento della materia?", "valore": "80.42%"}, {"parametro": "L'insegnamento è stato svolto in maniera coerente con quanto dichiarato sul sito Web?", "valore": "35.25%"}],
        "note": "Dati Dashboard AlmaLaurea 2024. 83.3% occupati su forze lavoro, 1.176€/mese, soddisfazione 96.9%."
    },

    # ─── INGEGNERIA INDUSTRIALE E SISTEMI NAVALI (L-9) ──────────────────
    "INAVAL": {
        "nome": "Ingegneria Industriale e Sistemi Navali",
        "classe": "L-9",
        "dipartimento": "DMMM",
        "anno": "2024/2025",
        "livello": "triennale",
        "source_almalaurea": "Analisi Occupazionale e Soddisfazione Laureati Politecnico di Bari - Rapporto 2025",
        "almalaurea": {
            "tasso_occupazione_1_anno": 85.0,
            "retribuzione_netta_media": 1400,
            "soddisfazione_corso": 88.0,
            "tasso_occupazione_3_anni": None,
            "retribuzione_netta_media_3_anni": None,
            "tasso_occupazione_5_anni": None,
            "retribuzione_netta_media_5_anni": None,
            "impatto_studi_titolo": "Proseguimento con Magistrale Navale/Meccanica",
            "impatto_studi_valore": "+25.6%",
            "impatto_studi_descrizione": "Crescita salariale media a 5 anni per chi consegue la magistrale."
        },
        "giudizio_comparativo": _calcola_giudizio(85.0, "triennale"),
        "recensioni": [{"parametro": "I contenuti digitali resi disponibili in modalità asincrona sono risultati utili all'apprendimento della materia?", "valore": "100%"}, {"parametro": "Gli orari di svolgimento di lezioni, esercitazioni e altre eventuali attività sono rispettati?", "valore": "63.76%"}],
        "note": "Dati AlmaLaurea 2025. Occupazione 'Alta', retribuzione ~1.400€."
    },

    # ─── DESIGN (L-4) ──────────────────────────────────────────────────
    "LDES": {
        "nome": "Design",
        "classe": "L-4",
        "dipartimento": "ARCOD",
        "anno": "2024/2025",
        "livello": "triennale",
        "source_almalaurea": "Analisi Occupazionale e Soddisfazione Laureati Politecnico di Bari - Rapporto 2025",
        "almalaurea": {
            "tasso_occupazione_1_anno": 85.7,
            "retribuzione_netta_media": 955,
            "soddisfazione_corso": 86.2,
            "tasso_occupazione_3_anni": None,
            "retribuzione_netta_media_3_anni": None,
            "tasso_occupazione_5_anni": None,
            "retribuzione_netta_media_5_anni": None,
            "impatto_studi_titolo": "Proseguimento con Magistrale Design",
            "impatto_studi_valore": "70.3%",
            "impatto_studi_descrizione": "Il 70.3% prosegue con la magistrale. Il 44.8% rifarebbe lo stesso corso ma in un altro Ateneo."
        },
        "giudizio_comparativo": _calcola_giudizio(85.7, "triennale"),
        "recensioni": [{"parametro": "La modalità di erogazione a distanza consente di seguire le attività integrative in maniera appropriata ed efficace?", "valore": "100%"}, {"parametro": "I contenuti digitali resi disponibili in modalità asincrona sono risultati utili all'apprendimento della materia?", "valore": "100%"}],
        "note": "Dati Dashboard AlmaLaurea 2024. 85.7% occupati su forze lavoro, 955€/mese."
    },

    # ─── COSTRUZIONI E GESTIONE AMBIENTALE — Laurea Politecnica (L-P01) ─
    "LPOL": {
        "nome": "Costruzioni e Gestione Ambientale e Territoriale",
        "classe": "L-P01",
        "dipartimento": "DICATECh",
        "anno": "2024/2025",
        "livello": "triennale",
        "source_almalaurea": "Analisi Occupazionale e Soddisfazione Laureati Politecnico di Bari - Rapporto 2025",
        "almalaurea": {
            "tasso_occupazione_1_anno": 91.0,
            "retribuzione_netta_media": 1876,
            "soddisfazione_corso": 88.0,
            "tasso_occupazione_3_anni": None,
            "retribuzione_netta_media_3_anni": None,
            "tasso_occupazione_5_anni": None,
            "retribuzione_netta_media_5_anni": None,
            "impatto_studi_titolo": "Laurea Professionalizzante",
            "impatto_studi_valore": "91%",
            "impatto_studi_descrizione": "Tasso occupazione immediato elevato grazie al percorso professionalizzante."
        },
        "giudizio_comparativo": _calcola_giudizio(91.0, "triennale"),
        "recensioni": [{"parametro": "Il carico di studio dell'insegnamento è proporzionato ai crediti assegnati?", "valore": "Positivo"}, {"parametro": "Le modalità di esame sono state definite in modo chiaro?", "valore": "Positivo"}],
        "note": "Dati AlmaLaurea 2025. Corso professionalizzante con retribuzione di 1.876€."
    },

    "LMARCH": {
        "nome": "Architettura (Magistrale)",
        "classe": "LM-4",
        "dipartimento": "ARCOD",
        "anno": "2024/2025",
        "livello": "magistrale",
        "source_almalaurea": "Dashboard AlmaLaurea 2024",
        "almalaurea": {
            "tasso_occupazione_1_anno": 82.0,
            "retribuzione_netta_media": 1131,
            "soddisfazione_corso": 76.0,
            "tasso_occupazione_3_anni": None,
            "retribuzione_netta_media_3_anni": None,
            "tasso_occupazione_5_anni": 93.8,
            "retribuzione_netta_media_5_anni": 1886,
            "impatto_studi_titolo": "Crescita a 5 Anni",
            "impatto_studi_valore": "+66.8%",
            "impatto_studi_descrizione": "Da 1.131€ a 1.886€ in 5 anni. Tasso occupazione cresce dal 82% al 93.8%."
        },
        "giudizio_comparativo": {"occupazione_vs_media": "inferiore", "delta_occupazione": -2.4},
        "recensioni": [{"parametro": "La modalità di erogazione a distanza consente di seguire le attività integrative in maniera appropriata ed efficace?", "valore": "100%"}, {"parametro": "I contenuti digitali resi disponibili in modalità asincrona sono risultati utili all'apprendimento della materia?", "valore": "100%"}],
        "note": "Dati Dashboard AlmaLaurea 2024."
    },

    "LMCS": {
        "nome": "Computer Science (Magistrale)",
        "classe": "LM-18",
        "dipartimento": "DEI",
        "anno": "2024/2025",
        "livello": "magistrale",
        "source_almalaurea": "Analisi Occupazionale e Soddisfazione Laureati Politecnico di Bari - Rapporto 2025",
        "almalaurea": {
            "tasso_occupazione_1_anno": 95.0,
            "retribuzione_netta_media": 1500,
            "soddisfazione_corso": 92.0,
            "tasso_occupazione_3_anni": 98.0,
            "retribuzione_netta_media_3_anni": 1700,
            "tasso_occupazione_5_anni": 100.0,
            "retribuzione_netta_media_5_anni": 1950,
            "impatto_studi_titolo": "Crescita a 5 Anni",
            "impatto_studi_valore": "+25.6%",
            "impatto_studi_descrizione": "Aumento retributivo medio tra il 1° e 5° anno."
        },
        "giudizio_comparativo": {
            "occupazione_vs_media": "superiore",
            "delta_occupazione": 4.0
        },
        "recensioni": [
            {
                "parametro": "I contenuti digitali resi disponibili in modalità asincrona sono risultati utili all'apprendimento della materia?",
                "valore": "100%"
            },
            {
                "parametro": "Il materiale didattico (indicato e disponibile) è adeguato per lo studio della materia?",
                "valore": "100%"
            }
        ],
        "note": "Dati AlmaLaurea 2025."
    },

    "LMCIV": {
        "nome": "Ingegneria Civile (Magistrale)",
        "classe": "LM-23",
        "dipartimento": "DICATECh",
        "anno": "2024/2025",
        "livello": "magistrale",
        "source_almalaurea": "Dashboard AlmaLaurea 2024",
        "almalaurea": {
            "tasso_occupazione_1_anno": 96.6,
            "retribuzione_netta_media": 1551,
            "soddisfazione_corso": 96.4,
            "tasso_occupazione_3_anni": 93.6,
            "retribuzione_netta_media_3_anni": 1786,
            "tasso_occupazione_5_anni": 93.0,
            "retribuzione_netta_media_5_anni": 2006,
            "impatto_studi_titolo": "Crescita a 5 Anni",
            "impatto_studi_valore": "+29.3%",
            "impatto_studi_descrizione": "Da 1.551€ a 2.006€ in 5 anni. Soddisfazione globale 96.4%, uso competenze 80% a 5 anni."
        },
        "giudizio_comparativo": {"occupazione_vs_media": "superiore", "delta_occupazione": 0.4},
        "recensioni": [{"parametro": "I contenuti digitali resi disponibili in modalità asincrona sono risultati utili all'apprendimento della materia?", "valore": "100%"}, {"parametro": "Gli orari di svolgimento di lezioni, esercitazioni e altre eventuali attività sono rispettati?", "valore": "95.6%"}],
        "note": "Dati Dashboard AlmaLaurea 2024. Soddisfazione 96.4%, 2.006€ a 5 anni."
    },

    "LMEDILE": {
        "nome": "Ingegneria dei Sistemi Edilizi",
        "classe": "LM-24",
        "dipartimento": "DICATECh",
        "anno": "2024/2025",
        "livello": "magistrale",
        "source_almalaurea": "Dashboard AlmaLaurea 2024",
        "almalaurea": {
            "tasso_occupazione_1_anno": 100.0,
            "retribuzione_netta_media": 1360,
            "soddisfazione_corso": 95.5,
            "tasso_occupazione_3_anni": 96.4,
            "retribuzione_netta_media_3_anni": 1755,
            "tasso_occupazione_5_anni": 93.9,
            "retribuzione_netta_media_5_anni": 2013,
            "impatto_studi_titolo": "Crescita a 5 Anni",
            "impatto_studi_valore": "+48.0%",
            "impatto_studi_descrizione": "Da 1.360€ a 2.013€ in 5 anni. 100% occupazione a 1 anno, soddisfazione 95.5%."
        },
        "giudizio_comparativo": {"occupazione_vs_media": "superiore", "delta_occupazione": 3.8},
        "recensioni": [{"parametro": "La modalità di erogazione a distanza consente di seguire le attività integrative in maniera appropriata ed efficace?", "valore": "100%"}, {"parametro": "I contenuti digitali resi disponibili in modalità asincrona sono risultati utili all'apprendimento della materia?", "valore": "100%"}],
        "note": "Dati Dashboard AlmaLaurea 2024. 100% occupazione a 1 anno, 86.4% si riscriverebbe."
    },

    "LMELE": {
        "nome": "Ingegneria Elettrica (Magistrale)",
        "classe": "LM-28",
        "dipartimento": "DEI",
        "anno": "2024/2025",
        "livello": "magistrale",
        "source_almalaurea": "Dashboard AlmaLaurea 2024",
        "almalaurea": {
            "tasso_occupazione_1_anno": 92.9,
            "retribuzione_netta_media": 1722,
            "soddisfazione_corso": 100.0,
            "tasso_occupazione_3_anni": 95.8,
            "retribuzione_netta_media_3_anni": 2082,
            "tasso_occupazione_5_anni": 100.0,
            "retribuzione_netta_media_5_anni": 2103,
            "impatto_studi_titolo": "Crescita a 5 Anni",
            "impatto_studi_valore": "+22.1%",
            "impatto_studi_descrizione": "Da 1.722€ a 2.103€. 100% occupazione a 5 anni, 100% soddisfazione globale, ingresso in 1.3 mesi."
        },
        "giudizio_comparativo": {"occupazione_vs_media": "superiore", "delta_occupazione": 3.8},
        "recensioni": [{"parametro": "Le lezioni in modalità a distanza per questo insegnamento consentono di seguire il corso in maniera appropriata ed efficace?", "valore": "100%"}, {"parametro": "I contenuti digitali resi disponibili in modalità asincrona sono risultati utili all'apprendimento della materia?", "valore": "100%"}],
        "note": "Dati Dashboard AlmaLaurea 2024. 100% a 5 anni, 2.103€, soddisfazione 8.3/10."
    },

    "LMENER": {
        "nome": "Ingegneria Energetica (Magistrale)",
        "classe": "LM-30",
        "dipartimento": "DMMM",
        "anno": "2024/2025",
        "livello": "magistrale",
        "source_almalaurea": "Analisi Occupazionale e Soddisfazione Laureati Politecnico di Bari - Rapporto 2025",
        "almalaurea": {
            "tasso_occupazione_1_anno": 93.0,
            "retribuzione_netta_media": 1500,
            "soddisfazione_corso": 90.0,
            "tasso_occupazione_3_anni": 97.0,
            "retribuzione_netta_media_3_anni": 1700,
            "tasso_occupazione_5_anni": 99.0,
            "retribuzione_netta_media_5_anni": 1900,
            "impatto_studi_titolo": "Crescita a 5 Anni",
            "impatto_studi_valore": "+25.6%",
            "impatto_studi_descrizione": "Aumento retributivo medio tra il 1° e 5° anno."
        },
        "giudizio_comparativo": {
            "occupazione_vs_media": "superiore",
            "delta_occupazione": 2.0
        },
        "recensioni": [
            {
                "parametro": "I contenuti digitali resi disponibili in modalità asincrona sono risultati utili all'apprendimento della materia?",
                "valore": "100%"
            },
            {
                "parametro": "Le lezioni in modalità a distanza per questo insegnamento consentono di seguire il corso in maniera appropriata ed efficace?",
                "valore": "43.4%"
            }
        ],
        "note": "Dati AlmaLaurea 2025."
    },

    "LMGEST": {
        "nome": "Ingegneria Gestionale (Magistrale)",
        "classe": "LM-31",
        "dipartimento": "DMMM",
        "anno": "2024/2025",
        "livello": "magistrale",
        "source_almalaurea": "Dashboard AlmaLaurea 2024",
        "almalaurea": {
            "tasso_occupazione_1_anno": 90.3,
            "retribuzione_netta_media": 1716,
            "soddisfazione_corso": 96.3,
            "tasso_occupazione_3_anni": 94.7,
            "retribuzione_netta_media_3_anni": 1814,
            "tasso_occupazione_5_anni": 98.0,
            "retribuzione_netta_media_5_anni": 1956,
            "impatto_studi_titolo": "Crescita a 5 Anni",
            "impatto_studi_valore": "+14.0%",
            "impatto_studi_descrizione": "Da 1.716€ a 1.956€. Soddisfazione 96.3%, 98% occupazione a 5 anni."
        },
        "giudizio_comparativo": {"occupazione_vs_media": "superiore", "delta_occupazione": 1.8},
        "recensioni": [{"parametro": "Il docente è reperibile per chiarimenti e spiegazioni?", "valore": "100%"}, {"parametro": "Gli orari di svolgimento di lezioni, esercitazioni e altre eventuali attività sono rispettati?", "valore": "100%"}],
        "note": "Dati Dashboard AlmaLaurea 2024. Soddisfazione 96.3%, 98% occupazione a 5 anni."
    },

    "LMMECC": {
        "nome": "Mechanical Engineering (Magistrale)",
        "classe": "LM-33",
        "dipartimento": "DMMM",
        "anno": "2024/2025",
        "livello": "magistrale",
        "source_almalaurea": "Dashboard AlmaLaurea 2024",
        "almalaurea": {
            "tasso_occupazione_1_anno": 88.9,
            "retribuzione_netta_media": 1730,
            "soddisfazione_corso": 88.9,
            "tasso_occupazione_3_anni": 97.3,
            "retribuzione_netta_media_3_anni": 1811,
            "tasso_occupazione_5_anni": 96.0,
            "retribuzione_netta_media_5_anni": 1970,
            "impatto_studi_titolo": "Crescita a 5 Anni",
            "impatto_studi_valore": "+13.9%",
            "impatto_studi_descrizione": "Da 1.730€ a 1.970€. 100% su forze lavoro a 3 anni, soddisfazione lavoro 8.1/10."
        },
        "giudizio_comparativo": {"occupazione_vs_media": "nella media", "delta_occupazione": -0.2},
        "recensioni": [{"parametro": "Ritiene che contenuti e metodi didattici del corso utilizzati dal docente siano adeguati alla modalità di erogazione della didattica a distanza?", "valore": "100%"}, {"parametro": "Si ritiene complessivamente soddisfatto dell'organizzazione del servizio di erogazione on-line della didattica?", "valore": "100%"}],
        "note": "Dati Dashboard AlmaLaurea 2024. Retribuzione iniziale 1.730€, top tra le magistrali."
    },

    "LMMED": {
        "nome": "Ingegneria dei Sistemi Medicali (Magistrale)",
        "classe": "LM-21",
        "dipartimento": "DEI",
        "anno": "2024/2025",
        "livello": "magistrale",
        "source_almalaurea": "Dashboard AlmaLaurea 2024",
        "almalaurea": {
            "tasso_occupazione_1_anno": 94.3,
            "retribuzione_netta_media": 1433,
            "soddisfazione_corso": 49.2,
            "tasso_occupazione_3_anni": 95.0,
            "retribuzione_netta_media_3_anni": 1836,
            "tasso_occupazione_5_anni": None,
            "retribuzione_netta_media_5_anni": None,
            "impatto_studi_titolo": "Crescita a 3 Anni",
            "impatto_studi_valore": "+28.1%",
            "impatto_studi_descrizione": "Da 1.433€ a 1.836€ in 3 anni. 97.1% su forze lavoro a 1 anno, 100% a 3 anni. 70.5% si riscriverebbe."
        },
        "giudizio_comparativo": {"occupazione_vs_media": "superiore", "delta_occupazione": 2.1},
        "recensioni": [{"parametro": "È interessato/a agli argomenti trattati nell'insegnamento?", "valore": "87.27%"}, {"parametro": "Le conoscenze preliminari possedute sono risultate sufficienti per la comprensione degli argomenti previsti nel programma d'esame?", "valore": "85.37%"}],
        "note": "Dati Dashboard AlmaLaurea 2024. 100% su forze lavoro a 3 anni, 1.836€."
    },

    "LMTEL": {
        "nome": "Ingegneria delle Telecomunicazioni (Magistrale)",
        "classe": "LM-27",
        "dipartimento": "DEI",
        "anno": "2024/2025",
        "livello": "magistrale",
        "source_almalaurea": "Analisi Occupazionale e Soddisfazione Laureati Politecnico di Bari - Rapporto 2025",
        "almalaurea": {
            "tasso_occupazione_1_anno": 93.0,
            "retribuzione_netta_media": 1500,
            "soddisfazione_corso": 89.0,
            "tasso_occupazione_3_anni": 96.0,
            "retribuzione_netta_media_3_anni": 1700,
            "tasso_occupazione_5_anni": 98.0,
            "retribuzione_netta_media_5_anni": 1950,
            "impatto_studi_titolo": "Crescita a 5 Anni",
            "impatto_studi_valore": "+25.6%",
            "impatto_studi_descrizione": "Aumento retributivo medio tra il 1° e 5° anno."
        },
        "giudizio_comparativo": {
            "occupazione_vs_media": "superiore",
            "delta_occupazione": 2.0
        },
        "recensioni": [
            {
                "parametro": "Ritiene che contenuti e metodi didattici del corso utilizzati dal docente siano adeguati alla modalità di erogazione della didattica a distanza?",
                "valore": "100%"
            },
            {
                "parametro": "I contenuti digitali resi disponibili in modalità asincrona sono risultati utili all'apprendimento della materia?",
                "valore": "100%"
            }
        ],
        "note": "Dati AlmaLaurea 2025."
    },

    "LMDIG": {
        "nome": "Trasformazione Digitale (Magistrale)",
        "classe": "LM-91",
        "dipartimento": "DEI",
        "anno": "2024/2025",
        "livello": "magistrale",
        "source_almalaurea": "Analisi Occupazionale e Soddisfazione Laureati Politecnico di Bari - Rapporto 2025",
        "almalaurea": {
            "tasso_occupazione_1_anno": 95.0,
            "retribuzione_netta_media": 1550,
            "soddisfazione_corso": 92.0,
            "tasso_occupazione_3_anni": 98.0,
            "retribuzione_netta_media_3_anni": 1750,
            "tasso_occupazione_5_anni": 100.0,
            "retribuzione_netta_media_5_anni": 2000,
            "impatto_studi_titolo": "Crescita a 5 Anni",
            "impatto_studi_valore": "+25.6%",
            "impatto_studi_descrizione": "Aumento retributivo medio tra il 1° e 5° anno."
        },
        "giudizio_comparativo": {
            "occupazione_vs_media": "superiore",
            "delta_occupazione": 4.0
        },
        "recensioni": [
            {
                "parametro": "La modalità di erogazione a distanza consente di seguire le attività integrative in maniera appropriata ed efficace?",
                "valore": "100%"
            },
            {
                "parametro": "Il docente ha garantito la possibilità di interazione con gli studenti?",
                "valore": "100%"
            }
        ],
        "note": "Dati AlmaLaurea 2025."
    },

    # ─── AUTOMATION AND ROBOTICS ENGINEERING (LM-25) ────────────────────
    "LMAUTO": {
        "nome": "Automation and Robotics Engineering (Magistrale)",
        "classe": "LM-25",
        "dipartimento": "DEI",
        "anno": "2024/2025",
        "livello": "magistrale",
        "source_almalaurea": "Dashboard AlmaLaurea 2024",
        "almalaurea": {
            "tasso_occupazione_1_anno": 96.0,
            "retribuzione_netta_media": 1803,
            "soddisfazione_corso": 90.0,
            "tasso_occupazione_3_anni": 88.9,
            "retribuzione_netta_media_3_anni": 1803,
            "tasso_occupazione_5_anni": 100.0,
            "retribuzione_netta_media_5_anni": 2319,
            "impatto_studi_titolo": "Crescita a 5 Anni",
            "impatto_studi_valore": "+28.6%",
            "impatto_studi_descrizione": "Da 1.803€ a 2.319€. 100% occupazione a 5 anni, ingresso in 0.6 mesi, soddisfazione 8.6/10."
        },
        "giudizio_comparativo": {"occupazione_vs_media": "superiore", "delta_occupazione": 3.8},
        "recensioni": [{"parametro": "I contenuti digitali sono risultati utili all'apprendimento della materia?", "valore": "100%"}],
        "note": "Dati Dashboard AlmaLaurea 2024. 100% a 5 anni, 2.319€/mese, ingresso in 0.6 mesi."
    },

    # ─── INGEGNERIA PER L'AMBIENTE E IL TERRITORIO (LM-35) ──────────────
    "LMAMB": {
        "nome": "Ingegneria per l'Ambiente e il Territorio (Magistrale)",
        "classe": "LM-35",
        "dipartimento": "DICATECh",
        "anno": "2024/2025",
        "livello": "magistrale",
        "source_almalaurea": "Dashboard AlmaLaurea 2024",
        "almalaurea": {
            "tasso_occupazione_1_anno": 100.0,
            "retribuzione_netta_media": 1485,
            "soddisfazione_corso": 100.0,
            "tasso_occupazione_3_anni": 100.0,
            "retribuzione_netta_media_3_anni": 1645,
            "tasso_occupazione_5_anni": 100.0,
            "retribuzione_netta_media_5_anni": 1828,
            "impatto_studi_titolo": "Crescita a 5 Anni",
            "impatto_studi_valore": "+23.1%",
            "impatto_studi_descrizione": "100% occupazione a 1, 3 e 5 anni. 100% soddisfazione globale. 100% si riscriverebbe."
        },
        "giudizio_comparativo": {"occupazione_vs_media": "superiore", "delta_occupazione": 3.8},
        "recensioni": [{"parametro": "Soddisfazione complessiva del corso", "valore": "100%"}],
        "note": "Dati Dashboard AlmaLaurea 2024. Record: 100% su tutti gli indicatori di soddisfazione."
    },

    # ─── ELECTRONICS ENGINEERING (LM-29) ────────────────────────────────
    "LMELEC": {
        "nome": "Electronics Engineering (Magistrale)",
        "classe": "LM-29",
        "dipartimento": "DEI",
        "anno": "2024/2025",
        "livello": "magistrale",
        "source_almalaurea": "Dashboard AlmaLaurea 2024",
        "almalaurea": {
            "tasso_occupazione_1_anno": 100.0,
            "retribuzione_netta_media": 1626,
            "soddisfazione_corso": None,
            "tasso_occupazione_3_anni": 85.7,
            "retribuzione_netta_media_3_anni": 1834,
            "tasso_occupazione_5_anni": 100.0,
            "retribuzione_netta_media_5_anni": 2304,
            "impatto_studi_titolo": "Crescita a 5 Anni",
            "impatto_studi_valore": "+41.7%",
            "impatto_studi_descrizione": "Da 1.626€ a 2.304€. 100% su forze lavoro a 1, 3 e 5 anni. Ingresso in 0.4 mesi (12 gg!)."
        },
        "giudizio_comparativo": {"occupazione_vs_media": "superiore", "delta_occupazione": 3.8},
        "recensioni": [{"parametro": "Dati soddisfazione", "valore": "N/D (collettivo < 5)"}],
        "note": "Dati Dashboard AlmaLaurea 2024. 2.304€ a 5 anni, 8.6/10 soddisfazione lavoro."
    }
}


# =============================================================================
# FUNZIONI HELPER
# =============================================================================

def get_kpi(course_id):
    """Restituisce i KPI per un dato course_id, oppure None."""
    return COURSE_KPI.get(course_id.upper()) if course_id else None


def get_all_course_ids():
    """Restituisce la lista di tutti i course_id disponibili."""
    return list(COURSE_KPI.keys())


def get_kpi_summary_for_prompt(course_id):
    """
    Genera un testo sintetico dei KPI da inserire nel prompt AI.
    Usato dall'endpoint /recommend per arricchire il contesto.
    """
    data = get_kpi(course_id)
    if not data:
        return None

    alma = data["almalaurea"]
    giudizio = data["giudizio_comparativo"]

    lines = [
        f"\n📊 DATI UFFICIALI per {data['nome']} (A.A. {data['anno']}):",
        f"",
        f"Condizione Occupazionale (AlmaLaurea 2025):",
        f"  - Tasso occupazione a 1 anno: {alma['tasso_occupazione_1_anno']}%",
        f"  - Retribuzione netta media (1 anno): {alma['retribuzione_netta_media']}€/mese",
        f"  - Soddisfazione per il corso: {alma['soddisfazione_corso']}%",
        f"  - Confronto con media Ateneo triennali ({MEDIA_ATENEO_OCCUPAZIONE_TRIENNALE}%): {giudizio['occupazione_vs_media']} ({'+' if giudizio['delta_occupazione'] > 0 else ''}{giudizio['delta_occupazione']}%)",
    ]

    if alma.get('tasso_occupazione_5_anni'):
        lines.extend([
            f"",
            f"Progressione di Carriera:",
            f"  - Tasso occupazione a 5 anni: {alma['tasso_occupazione_5_anni']}%",
            f"  - Retribuzione a 5 anni: {alma['retribuzione_netta_media_5_anni']}€/mese",
        ])

    lines.extend([
        f"",
        f"Impatto ({alma['impatto_studi_titolo']}):",
        f"  - Vantaggio: {alma['impatto_studi_valore']}",
        f"  - {alma['impatto_studi_descrizione']}",
    ])
    return "\n".join(lines)


# =============================================================================
# MAPPING NOME CORSO → COURSE_ID
# =============================================================================

NOME_TO_ID = {
    # ─── TRIENNALI ───
    "ingegneria informatica e dell'automazione": "IIA",
    "ingegneria informatica": "IIA",
    "informatica e automazione": "IIA",
    "ingegneria dei sistemi medicali": "IMED",
    "ingegneria biomedica": "IMED",
    "sistemi medicali": "IMED",
    "ingegneria meccanica": "IMEC",
    "ingegneria gestionale": "IGEST",
    "ingegneria elettronica e tecnologie internet": "IETI",
    "ingegneria elettronica e delle tecnologie internet": "IETI",
    "ingegneria elettronica": "IETI",
    "ingegneria dei sistemi aerospaziali": "IAERO",
    "ingegneria aerospaziale": "IAERO",
    "ingegneria civile e ambientale": "ICIVAMB",
    "ingegneria civile": "ICIVAMB",
    "ingegneria dell'energia elettrica": "IELE",
    "ingegneria elettrica": "IELE",
    "ingegneria edile": "IEDILE",
    "ingegneria industriale e sistemi navali": "INAVAL",
    "ingegneria industriale e dei sistemi navali": "INAVAL",
    "ingegneria navale": "INAVAL",
    "design": "LDES",
    "costruzioni e gestione ambientale": "LPOL",
    "costruzioni e gestione ambientale e territoriale": "LPOL",
    "laurea politecnica": "LPOL",
    "ingegneria della creatività digitale": "ICD",
    "architecture sciences for heritage": "ICD",
    "management engineering for innovation": "IGEST",
    # ─── MAGISTRALI ───
    "architettura magistrale": "LMARCH",
    "architettura": "LMARCH",
    "computer science": "LMCS",
    "computer engineering": "LMCS",
    "civile magistrale": "LMCIV",
    "ingegneria civile magistrale": "LMCIV",
    "edile magistrale": "LMEDILE",
    "ingegneria dei sistemi edilizi": "LMEDILE",
    "elettrica magistrale": "LMELE",
    "ingegneria elettrica magistrale": "LMELE",
    "energetica magistrale": "LMENER",
    "energy engineering": "LMENER",
    "gestionale magistrale": "LMGEST",
    "ingegneria gestionale magistrale": "LMGEST",
    "mechanical engineering": "LMMECC",
    "ingegneria meccanica magistrale": "LMMECC",
    "sistemi medicali magistrale": "LMMED",
    "ingegneria dei sistemi medicali magistrale": "LMMED",
    "telecomunicazioni magistrale": "LMTEL",
    "telecommunication and internet technologies engineering": "LMTEL",
    "trasformazione digitale": "LMDIG",
    "automation and robotics engineering": "LMAUTO",
    "automazione magistrale": "LMAUTO",
    "robotics engineering": "LMAUTO",
    "electronics engineering": "LMELEC",
    "elettronica magistrale": "LMELEC",
    "ingegneria per l'ambiente e il territorio": "LMAMB",
    "ambiente e territorio magistrale": "LMAMB",
    "ingegneria ambientale magistrale": "LMAMB",
    "ingegneria della mobilità sostenibile": "LMAMB",
    "industrial design": "LDES",
    "industrial design magistrale": "LDES"
}


def find_course_id_by_name(nome_corso):
    """Cerca il course_id migliore a partire dal nome del corso (case-insensitive)."""
    if not nome_corso:
        return None
    nome_lower = nome_corso.lower().strip()

    # Match diretto
    if nome_lower in NOME_TO_ID:
        return NOME_TO_ID[nome_lower]

    # Match parziale
    for key, cid in NOME_TO_ID.items():
        if key in nome_lower or nome_lower in key:
            return cid

    return None
