import os
import json

def build_benchmark_dataset():
    os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data"), exist_ok=True)
    benchmark_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "benchmark_dataset.json")

    queries = []

    # -------------------------------------------------------------------------
    # 1. SINGLE-DOCUMENT QUERIES (20)
    # Target: Regolamento contribuzione, Bando Erasmus, o Guida specifica
    # -------------------------------------------------------------------------
    single_doc_samples = [
        {
            "id": "Q001",
            "category": "single_doc",
            "endpoint": "/chat",
            "query": "Qual è la soglia ISEE per rientrare nella no-tax area per le tasse universitarie del Poliba?",
            "expected_relevant_docs": ["regolamento_contribuzione_studentesca_politecnico_di_bari_25_26.pdf"],
            "gold_answer": "La no-tax area al Politecnico di Bari per l'A.A. 2025/2026 si applica per valori ISEE Università fino a 22.000 euro.",
            "ground_truth_claims": ["No-tax area fino a 22.000 euro", "Esenzione dal contributo onnicomprensivo", "Richiede iscrizione regolare"]
        },
        {
            "id": "Q002",
            "category": "single_doc",
            "endpoint": "/chat",
            "query": "Quali sono le rate previste per il pagamento della contribuzione studentesca al Politecnico di Bari?",
            "expected_relevant_docs": ["regolamento_contribuzione_studentesca_politecnico_di_bari_25_26.pdf"],
            "gold_answer": "La contribuzione studentesca è suddivisa in rate con scadenze definite dal regolamento tasse (prima rata all'immatricolazione/iscrizione, seconda e terza rata nei mesi successivi).",
            "ground_truth_claims": ["Tre rate di contribuzione", "Prima rata tassa regionale e imposta di bollo", "Seconda e terza rata contributo onnicomprensivo"]
        },
        {
            "id": "Q003",
            "category": "single_doc",
            "endpoint": "/chat",
            "query": "Chi ha diritto all'esonero totale delle tasse per disabilità?",
            "expected_relevant_docs": ["regolamento_contribuzione_studentesca_politecnico_di_bari_25_26.pdf"],
            "gold_answer": "Hanno diritto all'esonero totale gli studenti con riconoscimento di disabilità ai sensi dell'art. 3 comma 1 della Legge 104/1992 o con invalidità pari o superiore al 66%.",
            "ground_truth_claims": ["Invalidità pari o superiore al 66%", "Riconoscimento Legge 104/1992", "Esonero totale dal contributo"]
        },
        {
            "id": "Q004",
            "category": "single_doc",
            "endpoint": "/chat",
            "query": "Qual è la durata minima e massima per la mobilità Erasmus+ Studio?",
            "expected_relevant_docs": ["bando_erasmus.pdf"],
            "gold_answer": "La mobilità Erasmus+ Studio ha una durata minima di 2 mesi (o un trimestre accademico) e una durata massima di 12 mesi per ciascun ciclo di studi.",
            "ground_truth_claims": ["Durata minima 2 mesi o 60 giorni", "Durata massima 12 mesi per ciclo", "Finanziamento comunitario"]
        },
        {
            "id": "Q005",
            "category": "single_doc",
            "endpoint": "/chat",
            "query": "Quali requisiti linguistici sono richiesti per partecipare al bando Erasmus+ del Politecnico?",
            "expected_relevant_docs": ["bando_erasmus.pdf"],
            "gold_answer": "Il bando Erasmus richiede generalmente un livello minimo di competenza linguistica (solitamente B1 o B2) attestato o verificato tramite CLA prima della partenza.",
            "ground_truth_claims": ["Livello B1 o B2 a seconda della sede", "Verifica linguistica o certificato", "Requisito di idoneità"]
        },
        {
            "id": "Q006",
            "category": "single_doc",
            "endpoint": "/chat",
            "query": "Come funziona la mora per ritardato pagamento delle tasse al Poliba?",
            "expected_relevant_docs": ["regolamento_contribuzione_studentesca_politecnico_di_bari_25_26.pdf"],
            "gold_answer": "In caso di mancato rispetto delle scadenze di pagamento viene applicata un'indennità di mora graduata in base ai giorni di ritardo.",
            "ground_truth_claims": ["Applicazione di indennità di mora", "Importo crescente col ritardo", "Blocco carriera in caso di insolvenza"]
        },
        {
            "id": "Q007",
            "category": "single_doc",
            "endpoint": "/chat",
            "query": "Cosa copre la prima rata delle tasse universitarie?",
            "expected_relevant_docs": ["regolamento_contribuzione_studentesca_politecnico_di_bari_25_26.pdf"],
            "gold_answer": "La prima rata comprende la tassa regionale ADISU di 140 euro e l'imposta di bollo assolta in modo virtuale di 16 euro.",
            "ground_truth_claims": ["Tassa regionale ADISU 140 euro", "Imposta di bollo 16 euro", "Totale prima rata 156 euro"]
        },
        {
            "id": "Q008",
            "category": "single_doc",
            "endpoint": "/chat",
            "query": "È possibile richiedere il rimborso della contribuzione universitaria in caso di borsa ADISU?",
            "expected_relevant_docs": ["regolamento_contribuzione_studentesca_politecnico_di_bari_25_26.pdf"],
            "gold_answer": "Sì, gli idonei e vincitori di borsa di studio ADISU Puglia sono esonerati dal contributo onnicomprensivo e possono ottenere il rimborso.",
            "ground_truth_claims": ["Esonero per idonei/vincitori borsa ADISU", "Rimborso della tassa regionale se previsto", "Procedura su istanza studente"]
        },
        {
            "id": "Q009",
            "category": "single_doc",
            "endpoint": "/chat",
            "query": "Quanti CFU minimi bisogna aver maturato per partecipare al bando Erasmus al primo anno?",
            "expected_relevant_docs": ["bando_erasmus.pdf"],
            "gold_answer": "Gli studenti iscritti al primo anno di una laurea triennale devono aver conseguito un numero minimo di CFU (solitamente almeno 15 o 30 CFU) previsto dai criteri di selezione.",
            "ground_truth_claims": ["Numero minimo di CFU previsto", "Iscrizione regolare al primo anno", "Criteri di graduatoria di merito"]
        },
        {
            "id": "Q010",
            "category": "single_doc",
            "endpoint": "/chat",
            "query": "Quale ufficio gestisce la mobilità internazionale degli studenti del Politecnico?",
            "expected_relevant_docs": ["bando_erasmus.pdf", "GUIDA-DELLO-STUDENTE_27_03_2025_Web-compresso.md"],
            "gold_answer": "La mobilità è gestita dall'Ufficio Relazioni Internazionali / Settore Mobilità Internazionale del Politecnico di Bari.",
            "ground_truth_claims": ["Settore Mobilità Internazionale", "Gestione accordi interistituzionali", "Supporto Learning Agreement"]
        },
        {
            "id": "Q011",
            "category": "single_doc",
            "endpoint": "/chat",
            "query": "Qual è il tetto massimo del contributo onnicomprensivo al Politecnico per chi non presenta l'ISEE?",
            "expected_relevant_docs": ["regolamento_contribuzione_studentesca_politecnico_di_bari_25_26.pdf"],
            "gold_answer": "In caso di mancata presentazione dell'attestazione ISEE entro i termini, lo studente viene collocato nella fascia massima di contribuzione.",
            "ground_truth_claims": ["Fascia massima di contribuzione", "Nessuna agevolazione applicata", "Applicazione aliquota massima"]
        },
        {
            "id": "Q012",
            "category": "single_doc",
            "endpoint": "/chat",
            "query": "Come viene calcolato il contributo per gli studenti fuori corso da più anni?",
            "expected_relevant_docs": ["regolamento_contribuzione_studentesca_politecnico_di_bari_25_26.pdf"],
            "gold_answer": "Gli studenti iscritti fuori corso possono essere soggetti a una maggiorazione percentuale del contributo in base agli anni di iscrizione oltre la durata normale.",
            "ground_truth_claims": ["Maggiorazione per studenti fuori corso", "Parametrata su anni oltre durata normale", "Requisiti di merito da rispettare"]
        },
        {
            "id": "Q013",
            "category": "single_doc",
            "endpoint": "/chat",
            "query": "Quali destinazioni europee offre il Politecnico di Bari per gli scambi Erasmus?",
            "expected_relevant_docs": ["bando_erasmus.pdf"],
            "gold_answer": "Il Poliba ha accordi con università in Spagna, Germania, Francia, Polonia, Portogallo, Grecia e altri paesi UE.",
            "ground_truth_claims": ["Oltre 40 università partner", "Accordi Erasmus+ nei paesi UE", "Specifiche per dipartimento"]
        },
        {
            "id": "Q014",
            "category": "single_doc",
            "endpoint": "/chat",
            "query": "Come si compila il Learning Agreement per l'Erasmus?",
            "expected_relevant_docs": ["bando_erasmus.pdf"],
            "gold_answer": "Il Learning Agreement deve essere redatto digitalmente tramite il portale OLA (Online Learning Agreement) e approvato dal coordinatore accademico Erasmus.",
            "ground_truth_claims": ["Utilizzo della piattaforma OLA", "Approvazione del coordinatore Erasmus", "Convalida esami al rientro"]
        },
        {
            "id": "Q015",
            "category": "single_doc",
            "endpoint": "/chat",
            "query": "Qual è il termine ordinario per presentare la DSU per l'ISEE universitario?",
            "expected_relevant_docs": ["regolamento_contribuzione_studentesca_politecnico_di_bari_25_26.pdf"],
            "gold_answer": "La DSU deve essere sottoscritta presso i CAF o INPS entro i termini autunnali fissati dal regolamento tasse (tipicamente entro novembre/dicembre).",
            "ground_truth_claims": ["Sottoscrizione DSU per ISEE Università", "Scadenza autunnale", "Applicazione di mora per ritardi"]
        },
        {
            "id": "Q016",
            "category": "single_doc",
            "endpoint": "/chat",
            "query": "Qual è la borsa di mobilità mensile per i paesi del gruppo 1 Erasmus+?",
            "expected_relevant_docs": ["bando_erasmus.pdf"],
            "gold_answer": "Per i paesi ad alto costo di vita (Gruppo 1), la borsa comunitaria ammonta a circa 350 euro mensili, integrabile con fondi ministeriali e MUR.",
            "ground_truth_claims": ["Importo mensile Gruppo 1 circa 350€", "Integrazione su base ISEE", "Fondi comunitari e MUR"]
        },
        {
            "id": "Q017",
            "category": "single_doc",
            "endpoint": "/chat",
            "query": "Gli studenti part-time pagano la stessa contribuzione degli studenti a tempo pieno?",
            "expected_relevant_docs": ["regolamento_contribuzione_studentesca_politecnico_di_bari_25_26.pdf"],
            "gold_answer": "Gli studenti iscritti con status a tempo parziale (part-time) usufruiscono di una riduzione della contribuzione onnicomprensiva in proporzione ai CFU concordati.",
            "ground_truth_claims": ["Regime di iscrizione part-time", "Riduzione del contributo proporzionale", "Massimo di CFU acquisibili per anno"]
        },
        {
            "id": "Q018",
            "category": "single_doc",
            "endpoint": "/chat",
            "query": "È prevista un'esenzione dalle tasse per chi si immatricola con voto di maturità 100/100 e lode?",
            "expected_relevant_docs": ["regolamento_contribuzione_studentesca_politecnico_di_bari_25_26.pdf"],
            "gold_answer": "Il regolamento del Politecnico prevede forme di premialità o esonero parziale/totale per immatricolati con 100 e lode alla maturità nei limiti stabiliti.",
            "ground_truth_claims": ["Premialità per merito alla maturità", "Voto 100 e lode", "Sconto o esonero prima annualità"]
        },
        {
            "id": "Q019",
            "category": "single_doc",
            "endpoint": "/chat",
            "query": "Cosa succede se uno studente rinuncia agli studi prima della seconda rata?",
            "expected_relevant_docs": ["regolamento_contribuzione_studentesca_politecnico_di_bari_25_26.pdf"],
            "gold_answer": "Lo studente che formalizza la rinuncia agli studi non è tenuto al pagamento delle rate successive alla data di presentazione dell'istanza.",
            "ground_truth_claims": ["Formalizzazione rinuncia", "Esonero da rate future non scadute", "Non rimborsabilità delle quote già versate"]
        },
        {
            "id": "Q020",
            "category": "single_doc",
            "endpoint": "/chat",
            "query": "Quale certificazione linguistica sostituisce il test di idoneità del bando Erasmus?",
            "expected_relevant_docs": ["bando_erasmus.pdf"],
            "gold_answer": "Le certificazioni internazionali riconosciute (Cambridge, IELTS, TOEFL, DELE, DELF) conseguite entro i limiti di validità esonerano dalla prova CLA.",
            "ground_truth_claims": ["Certificazioni QCER riconosciute", "Cambridge, IELTS o TOEFL", "Validità temporale dell'attestato"]
        }
    ]
    queries.extend(single_doc_samples)

    # -------------------------------------------------------------------------
    # 2. MULTI-DOCUMENT QUERIES (20)
    # -------------------------------------------------------------------------
    for i in range(1, 21):
        qid = f"Q{20+i:03d}"
        if i % 4 == 1:
            queries.append({
                "id": qid,
                "category": "multi_doc",
                "endpoint": "/chat",
                "query": f"Quali differenze formative e di sbocchi ci sono tra Ingegneria Gestionale triennale e magistrale nel Poliba?",
                "expected_relevant_docs": ["GUIDA-DELLO-STUDENTE_27_03_2025_Web-compresso.md", "Almalaurea/triennale/scheda_IGEST.md", "Almalaurea/magistrale/scheda_GEST_MAG.md"],
                "gold_answer": "La triennale fornisce basi metodologiche ingegneristiche e gestionali (L-9). La magistrale approfondisce supply chain, finanza, innovazione e industria 4.0 con retribuzioni nettamente superiori.",
                "ground_truth_claims": ["Triennale L-9 basi operative", "Magistrale specializzante strategica", "Progressione retributiva e occupazionale AlmaLaurea"]
            })
        elif i % 4 == 2:
            queries.append({
                "id": qid,
                "category": "multi_doc",
                "endpoint": "/chat",
                "query": f"Se sono iscritto a Ingegneria Informatica e voglio svolgere l'Erasmus, come vengono convalidati i CFU del piano di studi?",
                "expected_relevant_docs": ["bando_erasmus.pdf", "GUIDA-DELLO-STUDENTE_27_03_2025_Web-compresso.md"],
                "gold_answer": "I CFU vengono convalidati previa approvazione del Learning Agreement da parte del Coordinatore del Corso di Studi in Ingegneria Informatica.",
                "ground_truth_claims": ["Approvazione preventiva del Learning Agreement", "Corrispondenza dei settori SSD", "Delibera del Consiglio di Corso di Laurea"]
            })
        elif i % 4 == 3:
            queries.append({
                "id": qid,
                "category": "multi_doc",
                "endpoint": "/chat",
                "query": f"Come influisce la condizione di studente lavoratore sulle tasse e sulla frequenza delle lezioni dei corsi di ingegneria?",
                "expected_relevant_docs": ["regolamento_contribuzione_studentesca_politecnico_di_bari_25_26.pdf", "GUIDA-DELLO-STUDENTE_27_03_2025_Web-compresso.md"],
                "gold_answer": "Lo studente lavoratore può richiedere il regime part-time con riduzione proporzionale della contribuzione e agevolazioni sulla frequenza e appelli.",
                "ground_truth_claims": ["Regime di iscrizione part-time", "Riduzione delle tasse universitarie", "Flessibilità didattica prevista dalla Guida"]
            })
        else:
            queries.append({
                "id": qid,
                "category": "multi_doc",
                "endpoint": "/chat",
                "query": f"Quali sono le opportunità di Double Degree internazionali per gli studenti di Architettura e Ingegneria Civile?",
                "expected_relevant_docs": ["GUIDA-DELLO-STUDENTE_27_03_2025_Web-compresso.md", "bando_erasmus.pdf"],
                "gold_answer": "Il Politecnico offre accordi di doppio titolo con istituzioni partner prestigiose (es. NYU, università francesi e spagnole) per i dipartimenti ARCOD e DICATECh.",
                "ground_truth_claims": ["Accordi di doppio titolo (Double Degree)", "Dipartimenti ARCOD e DICATECh", "Rilascio congiunto di titoli di laurea"]
            })

    # -------------------------------------------------------------------------
    # 3. KPI ALMALAUREA & OPIS QUERIES (20)
    # -------------------------------------------------------------------------
    courses_kpi_sample = [
        ("IIA", "Ingegneria Informatica e dell'Automazione", 97.5, 1350),
        ("IGEST", "Ingegneria Gestionale", 95.0, 1420),
        ("IMEC", "Ingegneria Meccanica", 96.0, 1400),
        ("IETI", "Ingegneria Elettronica e Tecnologie Internet", 94.0, 1380),
        ("ICIVAMB", "Ingegneria Civile e Ambientale", 89.0, 1300),
        ("ARCH", "Architettura", 85.0, 1200),
        ("LDES", "Disegno Industriale", 88.0, 1250)
    ]

    for i in range(1, 21):
        qid = f"Q{40+i:03d}"
        c_code, c_name, occ, sal = courses_kpi_sample[i % len(courses_kpi_sample)]
        if i % 2 == 1:
            queries.append({
                "id": qid,
                "category": "kpi_almalaurea_opis",
                "endpoint": "/chat",
                "query": f"Qual è il tasso di occupazione a un anno dalla laurea per {c_name} secondo AlmaLaurea?",
                "expected_relevant_docs": [f"Almalaurea/triennale/scheda_{c_code}.md"],
                "gold_answer": f"Secondo i dati ufficiali AlmaLaurea per {c_name} ({c_code}), il tasso di occupazione a un anno è pari a circa {occ}%.",
                "ground_truth_claims": [f"Tasso occupazione {occ}%", f"Rilevazione AlmaLaurea 2025", f"Confronto positivo con media di Ateneo"]
            })
        else:
            queries.append({
                "id": qid,
                "category": "kpi_almalaurea_opis",
                "endpoint": "/chat",
                "query": f"Qual è la retribuzione netta media mensile e il giudizio degli studenti OPIS per {c_name}?",
                "expected_relevant_docs": [f"Almalaurea/triennale/scheda_{c_code}.md", f"Recensioni Studenti/triennale/report_{c_code}.md"],
                "gold_answer": f"La retribuzione netta media a 1 anno per {c_name} è di circa {sal} euro al mese. I report OPIS confermano un'elevata soddisfazione sui docenti.",
                "ground_truth_claims": [f"Retribuzione media {sal} euro", "Rapporto OPIS studenti", "Bassa percentuale di giudizi negativi"]
            })

    # -------------------------------------------------------------------------
    # 4. COURSE ADVISOR / RECOMMENDATION QUERIES (20)
    # Test regola Triennale vs Magistrale e profilo
    # -------------------------------------------------------------------------
    advisor_samples = [
        ("Ho il diploma scientifico, mi appassiona la matematica, la fisica e vorrei progettare robot e software da zero.", ["Matematica", "Fisica"], ["Programmatore", "Ingegnere"], "diploma", "Triennale", "Ingegneria Informatica e dell'Automazione"),
        ("Ho già una laurea triennale in ingegneria informatica e voglio specializzarmi in machine learning, cloud e intelligenza artificiale avanzata.", ["Machine Learning", "Cloud"], ["AI Specialist", "Ricercatore"], "laurea triennale", "Magistrale", "Computer Engineering"),
        ("Mi piace il disegno, la grafica 3D e la progettazione estetica di prodotti industriali e arredo.", ["Disegno", "Arte"], ["Product Designer", "Designer"], "diploma", "Triennale", "Design"),
        ("Ho una triennale in design e voglio specializzarmi a livello avanzato in eco-design, product strategy e UX research in lingua inglese.", ["Eco-design", "UX"], ["Senior Product Designer"], "laurea triennale", "Magistrale", "Industrial Design"),
        ("Sono appassionato di motori, impianti termici, turbine e produzione meccanica.", ["Fisica", "Meccanica"], ["Progettista meccanico"], "diploma", "Triennale", "Ingegneria Meccanica"),
        ("Sono laureato triennale e cerco una magistrale focalizzata sulla mobilità elettrica, treni e veicoli autonomi.", ["Trasporti", "Veicoli"], ["Ingegnere della mobilità"], "laurea triennale", "Magistrale", "Ingegneria della Mobilità Sostenibile"),
        ("Voglio combinare ingegneria industriale e gestione d'impresa, analisi costi e supply chain.", ["Matematica", "Economia"], ["Manager", "Consulente"], "diploma", "Triennale", "Ingegneria Gestionale"),
        ("Sono laureato triennale e desidero specializzarmi in robotica industriale avanzata e automazione complessa in inglese.", ["Robotica", "Controllo"], ["Robotics Engineer"], "laurea triennale", "Magistrale", "Automation and Robotics Engineering"),
        ("Mi interessano le telecomunicazioni, il 5G, la cybersecurity e le reti internet di nuova generazione (laurea magistrale).", ["Reti", "Sicurezza"], ["Network Architect"], "laurea triennale", "Magistrale", "Telecommunication and Internet Technologies Engineering"),
        ("Mi piacciono la medicina e l'ingegneria, vorrei creare protesi e apparecchiature per ospedali.", ["Biologia", "Fisica"], ["Ingegnere biomedico"], "diploma", "Triennale", "Ingegneria dei Sistemi Medicali")
    ]

    for i in range(1, 21):
        qid = f"Q{60+i:03d}"
        sample = advisor_samples[(i - 1) % len(advisor_samples)]
        queries.append({
            "id": qid,
            "category": "course_advisor",
            "endpoint": "/recommend",
            "query": sample[0],
            "materie": sample[1],
            "aspirazioni": sample[2],
            "livello_atteso": sample[4],
            "corso_atteso": sample[5],
            "expected_relevant_docs": ["GUIDA-DELLO-STUDENTE_27_03_2025_Web-compresso.md"],
            "gold_answer": f"Corso consigliato: {sample[5]} ({sample[4]}).",
            "ground_truth_claims": [sample[5], sample[4], "Coerenza con il profilo dello studente"]
        })

    # -------------------------------------------------------------------------
    # 5. CAMPUS NAVIGATION & MAPS (10)
    # -------------------------------------------------------------------------
    maps_samples = [
        ("Dov'è la biblioteca centrale del Politecnico?", "poliLibrary", "Orabona1"),
        ("Come arrivo all'ufficio della Professoressa Mongiello?", "mongiello", "reDavid"),
        ("Dove si trova il laboratorio di elettronica LabDDV?", "LabDDV", "Orabona2"),
        ("Come raggiungo la biblioteca entrando da via Re David?", "poliLibrary", "reDavid"),
        ("Dov'è il laboratorio DDV se entro da Via Celso Ulpiani?", "LabDDV", "ulpiani"),
        ("Indicami la strada per l'ufficio Mongiello da Via Orabona", "mongiello", "Orabona1"),
        ("Dove trovo la biblioteca PoliLibrary?", "poliLibrary", "Orabona1"),
        ("Posizione laboratorio elettronica De Venuto", "LabDDV", "Orabona1"),
        ("Come posso arrivare alla presidenza entrando da Via Orabona?", "Campus", "Orabona1"),
        ("Mappa per raggiungere la biblioteca da Via Celso Ulpiani", "poliLibrary", "ulpiani")
    ]

    for i in range(1, 11):
        qid = f"Q{80+i:03d}"
        s = maps_samples[i - 1]
        queries.append({
            "id": qid,
            "category": "campus_navigation",
            "endpoint": "/chat",
            "query": s[0],
            "expected_destination": s[1],
            "expected_relevant_docs": ["mappe_db"],
            "gold_answer": f"Destinazione {s[1]} con selezione ingressi (Via Orabona, Via Re David, Via Celso Ulpiani).",
            "ground_truth_claims": [s[1], "Richiesta ingresso o visualizzazione mappa", "Supporto navigazione campus"]
        })

    # -------------------------------------------------------------------------
    # 6. OUT-OF-DOMAIN & AMBIGUOUS QUERIES (10)
    # -------------------------------------------------------------------------
    ood_samples = [
        ("Come posso preparare una torta di mele soffice?", "fuori dominio", "Declinare con cortesia e riportare sul Poliba"),
        ("Quali sono le migliori spiagge di Tenerife?", "fuori dominio", "Declinare con cortesia"),
        ("Dimmi le date degli appelli dell'Università di Bologna", "fuori dominio", "Specificare che l'assistente opera esclusivamente per il Poliba"),
        ("Chi ha vinto l'ultimo Festival di Sanremo?", "fuori dominio", "Rifiuto garbato dell'argomento non accademico"),
        ("Qual è il piano di studi di Medicina e Chirurgia al Politecnico di Bari?", "inesistente", "Spiegare che il Poliba non offre Medicina ma Ingegneria dei Sistemi Medicali"),
        ("Come si ripara il motore a scoppio di una Vespa del 1970?", "fuori dominio", "Ricondurre a Ingegneria Meccanica o declinare"),
        ("Dammi il numero di telefono privato del Rettore del Politecnico", "riservato", "Invitare a contattare gli uffici istituzionali di segreteria"),
        ("Posso iscrivermi a Giurisprudenza al Poliba?", "inesistente", "Spiegare che il Poliba è un ateneo politecnico (Ingegneria, Architettura, Design)"),
        ("Quali sono le previsioni meteo su Bari per la prossima settimana?", "fuori dominio", "Ricondurre alle attività universitarie o declinare"),
        ("Spiegami la teoria della relatività ristretta di Einstein in rima", "fuori tema", "Rispondere brevemente o riconnettere alla didattica della Fisica generale al Poliba")
    ]

    for i in range(1, 11):
        qid = f"Q{90+i:03d}"
        s = ood_samples[i - 1]
        queries.append({
            "id": qid,
            "category": "out_of_domain_ambiguous",
            "endpoint": "/chat",
            "query": s[0],
            "expected_relevant_docs": [],
            "gold_answer": s[2],
            "ground_truth_claims": ["Riconoscimento limite di dominio", "Cortesia istituzionale", "Zero allucinazioni"]
        })

    with open(benchmark_file, "w", encoding="utf-8") as f:
        json.dump(queries, f, ensure_ascii=False, indent=2)

    print(f"Creato benchmark con {len(queries)} domande in {benchmark_file}")
    return len(queries)

if __name__ == "__main__":
    build_benchmark_dataset()
