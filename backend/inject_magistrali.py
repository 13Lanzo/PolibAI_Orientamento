import json
import re

magistrali_data = {
    'LMARCH': {
        "nome": "Architettura (Magistrale)",
        "classe": "LM-4",
        "dipartimento": "ARCOD",
        "anno": "2024/2025",
        "livello": "magistrale",
        "source_almalaurea": "Analisi Occupazionale e Soddisfazione Laureati Politecnico di Bari - Rapporto 2025",
        "almalaurea": {
            "tasso_occupazione_1_anno": 91.0,
            "retribuzione_netta_media": 1400,
            "soddisfazione_corso": 90.0,
            "tasso_occupazione_3_anni": 95.0,
            "retribuzione_netta_media_3_anni": 1550,
            "tasso_occupazione_5_anni": 98.0,
            "retribuzione_netta_media_5_anni": 1758,
            "impatto_studi_titolo": "Crescita a 5 Anni",
            "impatto_studi_valore": "+25.6%",
            "impatto_studi_descrizione": "Aumento retributivo medio tra il 1° e 5° anno."
        },
        "giudizio_comparativo": {"occupazione_vs_media": "nella media", "delta_occupazione": 0.0},
        "recensioni": [{"parametro": "La modalità di erogazione a distanza consente di seguire le attività integrative in maniera appropriata ed efficace?", "valore": "100%"}, {"parametro": "I contenuti digitali resi disponibili in modalità asincrona sono risultati utili all'apprendimento della materia?", "valore": "100%"}],
        "note": "Dati AlmaLaurea 2025."
    },
    'LMCS': {
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
            "impatto_studi_valore": "+30.0%",
            "impatto_studi_descrizione": "Aumento retributivo medio tra il 1° e 5° anno."
        },
        "giudizio_comparativo": {"occupazione_vs_media": "superiore", "delta_occupazione": 4.0},
        "recensioni": [{"parametro": "I contenuti digitali resi disponibili in modalità asincrona sono risultati utili all'apprendimento della materia?", "valore": "100%"}, {"parametro": "Il materiale didattico (indicato e disponibile) è adeguato per lo studio della materia?", "valore": "100%"}],
        "note": "Dati AlmaLaurea 2025."
    },
    'LMCIV': {
        "nome": "Ingegneria Civile (Magistrale)",
        "classe": "LM-23",
        "dipartimento": "DICATECh",
        "anno": "2024/2025",
        "livello": "magistrale",
        "source_almalaurea": "Analisi Occupazionale e Soddisfazione Laureati Politecnico di Bari - Rapporto 2025",
        "almalaurea": {
            "tasso_occupazione_1_anno": 90.0,
            "retribuzione_netta_media": 1400,
            "soddisfazione_corso": 85.0,
            "tasso_occupazione_3_anni": 94.0,
            "retribuzione_netta_media_3_anni": 1600,
            "tasso_occupazione_5_anni": 97.0,
            "retribuzione_netta_media_5_anni": 1800,
            "impatto_studi_titolo": "Crescita a 5 Anni",
            "impatto_studi_valore": "+28.6%",
            "impatto_studi_descrizione": "Aumento retributivo medio tra il 1° e 5° anno."
        },
        "giudizio_comparativo": {"occupazione_vs_media": "inferiore", "delta_occupazione": -1.0},
        "recensioni": [{"parametro": "I contenuti digitali resi disponibili in modalità asincrona sono risultati utili all'apprendimento della materia?", "valore": "100%"}, {"parametro": "Gli orari di svolgimento di lezioni, esercitazioni e altre eventuali attività sono rispettati?", "valore": "95.6%"}],
        "note": "Dati AlmaLaurea 2025."
    },
    'LMEDILE': {
        "nome": "Ingegneria dei Sistemi Edilizi",
        "classe": "LM-24",
        "dipartimento": "DICATECh",
        "anno": "2024/2025",
        "livello": "magistrale",
        "source_almalaurea": "Analisi Occupazionale e Soddisfazione Laureati Politecnico di Bari - Rapporto 2025",
        "almalaurea": {
            "tasso_occupazione_1_anno": 91.0,
            "retribuzione_netta_media": 1400,
            "soddisfazione_corso": 88.0,
            "tasso_occupazione_3_anni": 95.0,
            "retribuzione_netta_media_3_anni": 1600,
            "tasso_occupazione_5_anni": 97.0,
            "retribuzione_netta_media_5_anni": 1800,
            "impatto_studi_titolo": "Crescita a 5 Anni",
            "impatto_studi_valore": "+28.6%",
            "impatto_studi_descrizione": "Aumento retributivo medio tra il 1° e 5° anno."
        },
        "giudizio_comparativo": {"occupazione_vs_media": "nella media", "delta_occupazione": 0.0},
        "recensioni": [{"parametro": "La modalità di erogazione a distanza consente di seguire le attività integrative in maniera appropriata ed efficace?", "valore": "100%"}, {"parametro": "I contenuti digitali resi disponibili in modalità asincrona sono risultati utili all'apprendimento della materia?", "valore": "100%"}],
        "note": "Dati AlmaLaurea 2025."
    },
    'LMELE': {
        "nome": "Ingegneria dell'Energia Elettrica (Magistrale)",
        "classe": "LM-28",
        "dipartimento": "DEI",
        "anno": "2024/2025",
        "livello": "magistrale",
        "source_almalaurea": "Analisi Occupazionale e Soddisfazione Laureati Politecnico di Bari - Rapporto 2025",
        "almalaurea": {
            "tasso_occupazione_1_anno": 92.0,
            "retribuzione_netta_media": 1450,
            "soddisfazione_corso": 89.0,
            "tasso_occupazione_3_anni": 96.0,
            "retribuzione_netta_media_3_anni": 1650,
            "tasso_occupazione_5_anni": 98.0,
            "retribuzione_netta_media_5_anni": 1850,
            "impatto_studi_titolo": "Crescita a 5 Anni",
            "impatto_studi_valore": "+27.6%",
            "impatto_studi_descrizione": "Aumento retributivo medio tra il 1° e 5° anno."
        },
        "giudizio_comparativo": {"occupazione_vs_media": "superiore", "delta_occupazione": 1.0},
        "recensioni": [{"parametro": "Le lezioni in modalità a distanza per questo insegnamento consentono di seguire il corso in maniera appropriata ed efficace?", "valore": "100%"}, {"parametro": "I contenuti digitali resi disponibili in modalità asincrona sono risultati utili all'apprendimento della materia?", "valore": "100%"}],
        "note": "Dati AlmaLaurea 2025."
    },
    'LMENER': {
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
            "impatto_studi_valore": "+26.7%",
            "impatto_studi_descrizione": "Aumento retributivo medio tra il 1° e 5° anno."
        },
        "giudizio_comparativo": {"occupazione_vs_media": "superiore", "delta_occupazione": 2.0},
        "recensioni": [{"parametro": "I contenuti digitali resi disponibili in modalità asincrona sono risultati utili all'apprendimento della materia?", "valore": "100%"}, {"parametro": "Le lezioni in modalità a distanza per questo insegnamento consentono di seguire il corso in maniera appropriata ed efficace?", "valore": "43.4%"}],
        "note": "Dati AlmaLaurea 2025."
    },
    'LMGEST': {
        "nome": "Ingegneria Gestionale (Magistrale)",
        "classe": "LM-31",
        "dipartimento": "DMMM",
        "anno": "2024/2025",
        "livello": "magistrale",
        "source_almalaurea": "Analisi Occupazionale e Soddisfazione Laureati Politecnico di Bari - Rapporto 2025",
        "almalaurea": {
            "tasso_occupazione_1_anno": 94.0,
            "retribuzione_netta_media": 1550,
            "soddisfazione_corso": 91.0,
            "tasso_occupazione_3_anni": 97.0,
            "retribuzione_netta_media_3_anni": 1750,
            "tasso_occupazione_5_anni": 99.0,
            "retribuzione_netta_media_5_anni": 2000,
            "impatto_studi_titolo": "Crescita a 5 Anni",
            "impatto_studi_valore": "+29.0%",
            "impatto_studi_descrizione": "Aumento retributivo medio tra il 1° e 5° anno."
        },
        "giudizio_comparativo": {"occupazione_vs_media": "superiore", "delta_occupazione": 3.0},
        "recensioni": [{"parametro": "Il docente è reperibile per chiarimenti e spiegazioni?", "valore": "100%"}, {"parametro": "Gli orari di svolgimento di lezioni, esercitazioni e altre eventuali attività sono rispettati?", "valore": "100%"}],
        "note": "Dati AlmaLaurea 2025."
    },
    'LMMECC': {
        "nome": "Mechanical Engineering (Magistrale)",
        "classe": "LM-33",
        "dipartimento": "DMMM",
        "anno": "2024/2025",
        "livello": "magistrale",
        "source_almalaurea": "Analisi Occupazionale e Soddisfazione Laureati Politecnico di Bari - Rapporto 2025",
        "almalaurea": {
            "tasso_occupazione_1_anno": 92.0,
            "retribuzione_netta_media": 1500,
            "soddisfazione_corso": 89.0,
            "tasso_occupazione_3_anni": 96.0,
            "retribuzione_netta_media_3_anni": 1700,
            "tasso_occupazione_5_anni": 98.0,
            "retribuzione_netta_media_5_anni": 1950,
            "impatto_studi_titolo": "Crescita a 5 Anni",
            "impatto_studi_valore": "+30.0%",
            "impatto_studi_descrizione": "Aumento retributivo medio tra il 1° e 5° anno."
        },
        "giudizio_comparativo": {"occupazione_vs_media": "superiore", "delta_occupazione": 1.0},
        "recensioni": [{"parametro": "Ritiene che contenuti e metodi didattici del corso utilizzati dal docente siano adeguati alla modalità di erogazione della didattica a distanza?", "valore": "100%"}, {"parametro": "Si ritiene complessivamente soddisfatto dell'organizzazione del servizio di erogazione on-line della didattica?", "valore": "100%"}],
        "note": "Dati AlmaLaurea 2025."
    },
    'LMMED': {
        "nome": "Ingegneria dei Sistemi Medicali (Magistrale)",
        "classe": "LM-21",
        "dipartimento": "DEI",
        "anno": "2024/2025",
        "livello": "magistrale",
        "source_almalaurea": "Analisi Occupazionale e Soddisfazione Laureati Politecnico di Bari - Rapporto 2025",
        "almalaurea": {
            "tasso_occupazione_1_anno": 91.0,
            "retribuzione_netta_media": 1450,
            "soddisfazione_corso": 90.0,
            "tasso_occupazione_3_anni": 95.0,
            "retribuzione_netta_media_3_anni": 1650,
            "tasso_occupazione_5_anni": 98.0,
            "retribuzione_netta_media_5_anni": 1850,
            "impatto_studi_titolo": "Crescita a 5 Anni",
            "impatto_studi_valore": "+27.6%",
            "impatto_studi_descrizione": "Aumento retributivo medio tra il 1° e 5° anno."
        },
        "giudizio_comparativo": {"occupazione_vs_media": "nella media", "delta_occupazione": 0.0},
        "recensioni": [{"parametro": "È interessato/a agli argomenti trattati nell'insegnamento?", "valore": "87.27%"}, {"parametro": "Le conoscenze preliminari possedute sono risultate sufficienti per la comprensione degli argomenti previsti nel programma d'esame?", "valore": "85.37%"}],
        "note": "Dati AlmaLaurea 2025."
    },
    'LMTEL': {
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
            "impatto_studi_valore": "+30.0",
            "impatto_studi_descrizione": "Aumento retributivo medio tra il 1° e 5° anno."
        },
        "giudizio_comparativo": {"occupazione_vs_media": "superiore", "delta_occupazione": 2.0},
        "recensioni": [{"parametro": "Ritiene che contenuti e metodi didattici del corso utilizzati dal docente siano adeguati alla modalità di erogazione della didattica a distanza?", "valore": "100%"}, {"parametro": "I contenuti digitali resi disponibili in modalità asincrona sono risultati utili all'apprendimento della materia?", "valore": "100%"}],
        "note": "Dati AlmaLaurea 2025."
    },
    'LMDIG': {
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
            "impatto_studi_valore": "+29.0%",
            "impatto_studi_descrizione": "Aumento retributivo medio tra il 1° e 5° anno."
        },
        "giudizio_comparativo": {"occupazione_vs_media": "superiore", "delta_occupazione": 4.0},
        "recensioni": [{"parametro": "La modalità di erogazione a distanza consente di seguire le attività integrative in maniera appropriata ed efficace?", "valore": "100%"}, {"parametro": "Il docente ha garantito la possibilità di interazione con gli studenti?", "valore": "100%"}],
        "note": "Dati AlmaLaurea 2025."
    }
}

def inject():
    file_path = r"c:\Users\Lanzo\OneDrive\Desktop\progetto_sw\backend\kpi_data.py"
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Inserisco in COURSE_KPI
    end_of_dict = content.rfind('}')
    
    # We need to find the specific closing brace of COURSE_KPI
    # Actually simpler: append before the # =============================================================================
    # FUNZIONI HELPER
    
    idx = content.find('# FUNZIONI HELPER')
    insert_pos = content.rfind('}', 0, idx)
    
    new_entries = []
    for k, v in magistrali_data.items():
        v_str = json.dumps(v, indent=4, ensure_ascii=False)
        # Fix indentation
        v_str = "    " + v_str.replace('\n', '\n    ')
        new_entries.append(f'    "{k}": {v_str.strip()}')

    appended = ",\n\n" + ",\n\n".join(new_entries) + "\n"
    
    content = content[:insert_pos] + appended + content[insert_pos:]
    
    # Adesso aggiungiamo in NOME_TO_ID
    map_add = {
        "architettura magistrale": "LMARCH",
        "computer science": "LMCS",
        "civile magistrale": "LMCIV",
        "edile magistrale": "LMEDILE",
        "elettrica magistrale": "LMELE",
        "energetica magistrale": "LMENER",
        "gestionale magistrale": "LMGEST",
        "mechanical engineering": "LMMECC",
        "sistemi medicali magistrale": "LMMED",
        "telecomunicazioni magistrale": "LMTEL",
        "trasformazione digitale": "LMDIG"
    }
    
    idx_map = content.find('NOME_TO_ID = {')
    insert_map_pos = content.find('}', idx_map)
    
    new_maps = []
    for k, v in map_add.items():
        new_maps.append(f'    "{k}": "{v}"')
        
    app_maps = ",\n" + ",\n".join(new_maps) + "\n"
    content = content[:insert_map_pos] + app_maps + content[insert_map_pos:]
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    inject()
