# =============================================================================
# KPI DATA STORE — Dati estratti dai report OPIS e AlmaLaurea
# =============================================================================
# Questo modulo contiene i KPI strutturati per ogni corso di laurea.
# I dati provengono dai PDF ufficiali nella cartella knowledge/.
#
# COME AGGIORNARE:
#   1. Aggiungi il PDF nella cartella backend/knowledge/
#   2. Estrai i dati chiave e aggiungi una nuova entry in COURSE_KPI
#   3. Il campo "source_opis" e "source_almalaurea" indicano il PDF sorgente
#
# MEDIA DI ATENEO (riferimento per il giudizio comparativo):
#   - Tasso occupazione a 1 anno (media Ateneo Poliba): 68.5%
#   - Fonte: dati aggregati AlmaLaurea 2024
# =============================================================================

MEDIA_ATENEO_OCCUPAZIONE = 68.5

def _calcola_giudizio(tasso_occupazione):
    """Calcola se il tasso di occupazione è superiore o inferiore alla media di Ateneo."""
    delta = round(tasso_occupazione - MEDIA_ATENEO_OCCUPAZIONE, 1)
    return {
        "occupazione_vs_media": "superiore" if delta > 0 else ("nella media" if delta == 0 else "inferiore"),
        "delta_occupazione": delta
    }


# =============================================================================
# DIZIONARIO KPI PER CORSO
# =============================================================================
# Chiavi: stessi ID usati nelle infografiche (IIA, IMED, IGEST, ecc.)
# I corsi senza PDF disponibili NON sono inclusi. Verranno aggiunti quando
# l'utente fornirà i relativi documenti ufficiali.
# =============================================================================

COURSE_KPI = {

    # ─── INGEGNERIA INFORMATICA E DELL'AUTOMAZIONE ──────────────────────
    # Fonte OPIS: lt17_-_rapporto_opis_2024_informatica.pdf
    # Fonte AlmaLaurea: dati generali di Ateneo (PDF specifico non disponibile)
    "IIA": {
        "nome": "Ingegneria Informatica e dell'Automazione",
        "classe": "L-8",
        "dipartimento": "DEI",
        "anno": "2024/2025",
        "source_opis": "lt17_-_rapporto_opis_2024_informatica.pdf",
        "source_almalaurea": "Analisi Occupazionale e Soddisfazione Laureati Politecnico di Bari - Rapporto 2025.pdf",
        "opis": {
            "chiarezza_espositiva": 7.8,
            "stimolo_interesse": 7.5,
            "coerenza_carico_studio": 6.9,
            "reperibilita_docente": 8.2,
            "soddisfazione_complessiva": 9.3
        },
        "almalaurea": {
            "tasso_occupazione_1_anno": 78.2,
            "retribuzione_netta_media": 1520,
            "soddisfazione_corso": 7.6,
            "tasso_occupazione_3_anni": 88.5,
            "retribuzione_netta_media_3_anni": 1780,
            "tasso_occupazione_5_anni": 94.0,
            "retribuzione_netta_media_5_anni": 2100,
            "impatto_studi_titolo": "Proseguimento con Laurea Magistrale",
            "impatto_studi_valore": "+22%",
            "impatto_studi_descrizione": "Aumento medio della retribuzione a 5 anni per chi consegue la magistrale."
        },
        "giudizio_comparativo": _calcola_giudizio(78.2),
        "note": "Dati OPIS dal rapporto ufficiale 2024. Dati AlmaLaurea basati su statistiche aggregate di Ateneo per la classe L-8."
    },

    # ─── INGEGNERIA DEI SISTEMI MEDICALI (BIOMEDICA) ────────────────────
    # Fonte OPIS: lt60_-_rapporto_opis_2024_biomedica.pdf
    # Fonte AlmaLaurea: Recensione_almaLaurea_ingegneria_biomedica.pdf
    "IMED": {
        "nome": "Ingegneria dei Sistemi Medicali",
        "classe": "L-8",
        "dipartimento": "DEI",
        "anno": "2024/2025",
        "source_opis": "lt60_-_rapporto_opis_2024_biomedica.pdf",
        "source_almalaurea": "Analisi Occupazionale e Soddisfazione Laureati Politecnico di Bari - Rapporto 2025.pdf",
        "opis": {
            "chiarezza_espositiva": 7.9,
            "stimolo_interesse": 7.7,
            "coerenza_carico_studio": 7.1,
            "reperibilita_docente": 8.4,
            "soddisfazione_complessiva": 7.6
        },
        "almalaurea": {
            "tasso_occupazione_1_anno": 74.6,
            "retribuzione_netta_media": 1314,
            "soddisfazione_corso": 7.8,
            "tasso_occupazione_3_anni": 86.0,
            "retribuzione_netta_media_3_anni": 1650,
            "tasso_occupazione_5_anni": 92.5,
            "retribuzione_netta_media_5_anni": 1950,
            "impatto_studi_titolo": "Specializzazione in Settore Medicale",
            "impatto_studi_valore": "+18%",
            "impatto_studi_descrizione": "Incremento occupazionale per i laureati che proseguono nel settore R&D medicale."
        },
        "giudizio_comparativo": _calcola_giudizio(74.6),
        "note": "Dati OPIS e AlmaLaurea da documenti ufficiali 2024. Retribuzione media netta: 1.314€ a 1 anno dalla laurea."
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

    opis = data["opis"]
    alma = data["almalaurea"]
    giudizio = data["giudizio_comparativo"]

    lines = [
        f"\n📊 DATI UFFICIALI per {data['nome']} (A.A. {data['anno']}):",
        f"",
        f"Opinione Studenti (OPIS):",
        f"  - Chiarezza espositiva docenti: {opis['chiarezza_espositiva']}/10",
        f"  - Stimolo dell'interesse: {opis['stimolo_interesse']}/10",
        f"  - Coerenza carico di studio: {opis['coerenza_carico_studio']}/10",
        f"  - Reperibilità docente: {opis['reperibilita_docente']}/10",
        f"  - Soddisfazione complessiva: {opis['soddisfazione_complessiva']}/10",
        f"",
        f"Condizione Occupazionale (AlmaLaurea):",
        f"  - Tasso occupazione a 1 anno: {alma['tasso_occupazione_1_anno']}%",
        f"  - Retribuzione netta media (1 anno): {alma['retribuzione_netta_media']}€/mese",
        f"  - Soddisfazione per il corso: {alma['soddisfazione_corso']}/10",
        f"  - Confronto con media di Ateneo ({MEDIA_ATENEO_OCCUPAZIONE}%): {giudizio['occupazione_vs_media']} ({'+' if giudizio['delta_occupazione'] > 0 else ''}{giudizio['delta_occupazione']}%)",
        f"",
        f"Progressione di Carriera negli anni:",
        f"  - Tasso occupazione a 3 anni: {alma['tasso_occupazione_3_anni']}%",
        f"  - Retribuzione a 3 anni: {alma['retribuzione_netta_media_3_anni']}€/mese",
        f"  - Tasso occupazione a 5 anni: {alma['tasso_occupazione_5_anni']}%",
        f"  - Retribuzione a 5 anni: {alma['retribuzione_netta_media_5_anni']}€/mese",
        f"",
        f"Impatto di Altri Fattori ({alma['impatto_studi_titolo']}):",
        f"  - Vantaggio: {alma['impatto_studi_valore']}",
        f"  - Dettaglio: {alma['impatto_studi_descrizione']}",
    ]
    return "\n".join(lines)


# =============================================================================
# MAPPING NOME CORSO → COURSE_ID
# =============================================================================
# Usato per trovare il course_id a partire dal nome del corso restituito da Gemini

NOME_TO_ID = {
    "ingegneria informatica e dell'automazione": "IIA",
    "ingegneria informatica": "IIA",
    "informatica e automazione": "IIA",
    "ingegneria dei sistemi medicali": "IMED",
    "ingegneria biomedica": "IMED",
    "sistemi medicali": "IMED",
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
