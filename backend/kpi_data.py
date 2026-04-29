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
        "dipartimento": "DIEI",
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
            "impatto_studi_valore": "+25.6%",
            "impatto_studi_descrizione": "Crescita salariale media a 5 anni per chi consegue la magistrale al Poliba."
        },
        "giudizio_comparativo": _calcola_giudizio(97.5, "triennale"),
        "note": "Dati AlmaLaurea 2025. Miglior tasso di occupazione tra le triennali Poliba."
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
            "tasso_occupazione_1_anno": 85.0,
            "retribuzione_netta_media": 1350,
            "soddisfazione_corso": 88.0,
            "tasso_occupazione_3_anni": None,
            "retribuzione_netta_media_3_anni": None,
            "tasso_occupazione_5_anni": None,
            "retribuzione_netta_media_5_anni": None,
            "impatto_studi_titolo": "Specializzazione Magistrale (Medical Systems)",
            "impatto_studi_valore": "+25.6%",
            "impatto_studi_descrizione": "Crescita salariale media a 5 anni per chi consegue la magistrale al Poliba."
        },
        "giudizio_comparativo": _calcola_giudizio(85.0, "triennale"),
        "note": "Dati AlmaLaurea 2025. Dato occupazione indicato come 'Alta' nel rapporto, stimato ~85%."
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
            "soddisfazione_corso": 88.9,
            "tasso_occupazione_3_anni": None,
            "retribuzione_netta_media_3_anni": None,
            "tasso_occupazione_5_anni": None,
            "retribuzione_netta_media_5_anni": None,
            "impatto_studi_titolo": "Proseguimento con Magistrale (Mechanical Eng.)",
            "impatto_studi_valore": "+25.6%",
            "impatto_studi_descrizione": "Crescita salariale media a 5 anni per chi consegue la magistrale."
        },
        "giudizio_comparativo": _calcola_giudizio(88.9, "triennale"),
        "note": "Dati AlmaLaurea 2025. Retribuzione iniziale di 1.064€."
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
            "tasso_occupazione_1_anno": 85.0,
            "retribuzione_netta_media": 1350,
            "soddisfazione_corso": 88.0,
            "tasso_occupazione_3_anni": None,
            "retribuzione_netta_media_3_anni": None,
            "tasso_occupazione_5_anni": None,
            "retribuzione_netta_media_5_anni": None,
            "impatto_studi_titolo": "Proseguimento con Magistrale (Management Eng.)",
            "impatto_studi_valore": "+25.6%",
            "impatto_studi_descrizione": "Crescita salariale media a 5 anni per chi consegue la magistrale."
        },
        "giudizio_comparativo": _calcola_giudizio(85.0, "triennale"),
        "note": "Dati AlmaLaurea 2025. Tasso occupazione >85%, retribuzione 1.300-1.400€."
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
            "tasso_occupazione_1_anno": 90.0,
            "retribuzione_netta_media": 1350,
            "soddisfazione_corso": 88.0,
            "tasso_occupazione_3_anni": None,
            "retribuzione_netta_media_3_anni": None,
            "tasso_occupazione_5_anni": None,
            "retribuzione_netta_media_5_anni": None,
            "impatto_studi_titolo": "Proseguimento con Magistrale (Electronics Eng.)",
            "impatto_studi_valore": "+25.6%",
            "impatto_studi_descrizione": "Crescita salariale media a 5 anni per chi consegue la magistrale."
        },
        "giudizio_comparativo": _calcola_giudizio(90.0, "triennale"),
        "note": "Dati AlmaLaurea 2025. Tasso occupazione ~90%, retribuzione ~1.350€."
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
            "tasso_occupazione_1_anno": 85.0,
            "retribuzione_netta_media": 1400,
            "soddisfazione_corso": 92.0,
            "tasso_occupazione_3_anni": None,
            "retribuzione_netta_media_3_anni": None,
            "tasso_occupazione_5_anni": None,
            "retribuzione_netta_media_5_anni": None,
            "impatto_studi_titolo": "Proseguimento con Magistrale Aerospaziale",
            "impatto_studi_valore": "+25.6%",
            "impatto_studi_descrizione": "Crescita salariale media a 5 anni per chi consegue la magistrale."
        },
        "giudizio_comparativo": _calcola_giudizio(85.0, "triennale"),
        "note": "Dati AlmaLaurea 2025. Soddisfazione 'Molto Alta', retribuzione ~1.400€."
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
            "tasso_occupazione_1_anno": 77.5,
            "retribuzione_netta_media": 1250,
            "soddisfazione_corso": 82.0,
            "tasso_occupazione_3_anni": None,
            "retribuzione_netta_media_3_anni": None,
            "tasso_occupazione_5_anni": None,
            "retribuzione_netta_media_5_anni": None,
            "impatto_studi_titolo": "Proseguimento con Magistrale Civile",
            "impatto_studi_valore": "+25.6%",
            "impatto_studi_descrizione": "Crescita salariale media a 5 anni per chi consegue la magistrale."
        },
        "giudizio_comparativo": _calcola_giudizio(77.5, "triennale"),
        "note": "Dati AlmaLaurea 2025. Tasso occupazione 75-80%, retribuzione ~1.250€."
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
            "tasso_occupazione_1_anno": 85.0,
            "retribuzione_netta_media": 1350,
            "soddisfazione_corso": 82.0,
            "tasso_occupazione_3_anni": None,
            "retribuzione_netta_media_3_anni": None,
            "tasso_occupazione_5_anni": None,
            "retribuzione_netta_media_5_anni": None,
            "impatto_studi_titolo": "Proseguimento con Magistrale Elettrica",
            "impatto_studi_valore": "+25.6%",
            "impatto_studi_descrizione": "Crescita salariale media a 5 anni per chi consegue la magistrale."
        },
        "giudizio_comparativo": _calcola_giudizio(85.0, "triennale"),
        "note": "Dati AlmaLaurea 2025. Occupazione 'Alta', retribuzione ~1.350€."
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
            "tasso_occupazione_1_anno": 85.0,
            "retribuzione_netta_media": 1300,
            "soddisfazione_corso": 82.0,
            "tasso_occupazione_3_anni": None,
            "retribuzione_netta_media_3_anni": None,
            "tasso_occupazione_5_anni": None,
            "retribuzione_netta_media_5_anni": None,
            "impatto_studi_titolo": "Proseguimento con Magistrale Edile",
            "impatto_studi_valore": "+25.6%",
            "impatto_studi_descrizione": "Crescita salariale media a 5 anni per chi consegue la magistrale."
        },
        "giudizio_comparativo": _calcola_giudizio(85.0, "triennale"),
        "note": "Dati AlmaLaurea 2025. Occupazione 'Alta', retribuzione ~1.300€."
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
            "tasso_occupazione_1_anno": 61.0,
            "retribuzione_netta_media": 1100,
            "soddisfazione_corso": 75.0,
            "tasso_occupazione_3_anni": None,
            "retribuzione_netta_media_3_anni": None,
            "tasso_occupazione_5_anni": None,
            "retribuzione_netta_media_5_anni": None,
            "impatto_studi_titolo": "Proseguimento con Magistrale Design",
            "impatto_studi_valore": "+25.6%",
            "impatto_studi_descrizione": "Crescita salariale media a 5 anni per chi consegue la magistrale."
        },
        "giudizio_comparativo": _calcola_giudizio(61.0, "triennale"),
        "note": "Dati AlmaLaurea 2025. Occupazione ~61%, retribuzione ~1.100€."
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
        "note": "Dati AlmaLaurea 2025. Corso professionalizzante con retribuzione di 1.876€."
    },
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
    "ingegneria informatica e dell'automazione": "IIA",
    "ingegneria informatica": "IIA",
    "informatica e automazione": "IIA",
    "ingegneria dei sistemi medicali": "IMED",
    "ingegneria biomedica": "IMED",
    "sistemi medicali": "IMED",
    "ingegneria meccanica": "IMEC",
    "ingegneria gestionale": "IGEST",
    "ingegneria elettronica e tecnologie internet": "IETI",
    "ingegneria elettronica": "IETI",
    "ingegneria dei sistemi aerospaziali": "IAERO",
    "ingegneria aerospaziale": "IAERO",
    "ingegneria civile e ambientale": "ICIVAMB",
    "ingegneria civile": "ICIVAMB",
    "ingegneria dell'energia elettrica": "IELE",
    "ingegneria elettrica": "IELE",
    "ingegneria edile": "IEDILE",
    "ingegneria industriale e sistemi navali": "INAVAL",
    "ingegneria navale": "INAVAL",
    "design": "LDES",
    "costruzioni e gestione ambientale": "LPOL",
    "laurea politecnica": "LPOL",
    "ingegneria della creatività digitale": "ICD",
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
