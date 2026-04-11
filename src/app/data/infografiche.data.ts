/**
 * Catalogo COMPLETO delle infografiche precaricate nel frontend.
 *
 * Il backend decide QUANDO mostrarle restituendo il campo:
 *   { "infograficaId": "<id>" }
 *
 * Il frontend si occupa solo di recuperare i dati locali e renderizzarli.
 * NON analizza il testo, NON fa keyword matching: legge solo infograficaId.
 *
 * I path corrispondono ai file in public/assets/images/infografiche/
 */

export interface PercorsoCorrelato {
  label: string;
  value: string;
}

export interface InfograficaInfo {
  id: string;
  corso: string;
  path: string;
  percorsiCorrelati: PercorsoCorrelato[];
}

export const INFOGRAFICHE: InfograficaInfo[] = [

  // ── Classe L-8 ──────────────────────────────────────────────────────────

  {
    id: 'IIA',
    corso: "Ingegneria Informatica e dell'Automazione",
    path: 'assets/images/infografiche/ingegneria_informatica_automazione.jpg',
    percorsiCorrelati: [
      { label: "Ingegneria Informatica e dell'Automazione (L-8)", value: 'CORSO_IIA' },
      { label: 'Ingegneria della Creatività Digitale (L-8)',      value: 'CORSO_ICD'  },
      { label: 'Ingegneria Elettronica e Tecnologie Internet (L-8)', value: 'CORSO_IETI' },
    ],
  },

  {
    id: 'ICD',
    corso: 'Ingegneria della Creatività Digitale',
    path: 'assets/images/infografiche/ingegneria_creativita_digitale.jpg',
    percorsiCorrelati: [
      { label: 'Ingegneria della Creatività Digitale (L-8)',      value: 'CORSO_ICD'  },
      { label: "Ingegneria Informatica e dell'Automazione (L-8)", value: 'CORSO_IIA'  },
      { label: 'Ingegneria Elettronica e Tecnologie Internet (L-8)', value: 'CORSO_IETI' },
    ],
  },

  {
    id: 'IETI',
    corso: 'Ingegneria Elettronica e Tecnologie Internet',
    path: 'assets/images/infografiche/L8-IngegneriEletronicaeTecnologieInt.jpg',
    percorsiCorrelati: [
      { label: 'Ingegneria Elettronica e Tecnologie Internet (L-8)', value: 'CORSO_IETI' },
      { label: "Ingegneria Informatica e dell'Automazione (L-8)", value: 'CORSO_IIA'  },
      { label: 'Ingegneria della Creatività Digitale (L-8)',      value: 'CORSO_ICD'  },
    ],
  },

  // ── Classe L-7 / L-23 ──────────────────────────────────────────────────

  {
    id: 'ICIVAMB',
    corso: 'Ingegneria Civile e Ambientale',
    path: 'assets/images/infografiche/L7-ingegneriaCivileAmbientale.jpg',
    percorsiCorrelati: [
      { label: 'Ingegneria Civile e Ambientale (L-7)',  value: 'CORSO_ICIVAMB' },
      { label: 'Ingegneria Edile (L-23)',               value: 'CORSO_IEDILE'  },
    ],
  },

  {
    id: 'IEDILE',
    corso: 'Ingegneria Edile',
    path: 'assets/images/infografiche/ingegneria_edile.jpg',
    percorsiCorrelati: [
      { label: 'Ingegneria Edile (L-23)',               value: 'CORSO_IEDILE'  },
      { label: 'Ingegneria Civile e Ambientale (L-7)',  value: 'CORSO_ICIVAMB' },
    ],
  },

  // ── Classe L-9 ──────────────────────────────────────────────────────────

  {
    id: 'IELE',
    corso: 'Ingegneria Elettrica',
    path: 'assets/images/infografiche/L9-IngegneriElettrica.jpg',
    percorsiCorrelati: [
      { label: 'Ingegneria Elettrica (L-9)',            value: 'CORSO_IELE'   },
      { label: 'Ingegneria Meccanica (L-9)',            value: 'CORSO_IMEC'   },
      { label: 'Ingegneria Gestionale (L-9)',           value: 'CORSO_IGEST'  },
    ],
  },

  {
    id: 'IGEST',
    corso: 'Ingegneria Gestionale',
    path: 'assets/images/infografiche/L9-IngegneriGestionale.jpg',
    percorsiCorrelati: [
      { label: 'Ingegneria Gestionale (L-9)',           value: 'CORSO_IGEST'  },
      { label: 'Ingegneria Meccanica (L-9)',            value: 'CORSO_IMEC'   },
      { label: 'Ingegneria Elettrica (L-9)',            value: 'CORSO_IELE'   },
    ],
  },

  {
    id: 'IMEC',
    corso: 'Ingegneria Meccanica',
    path: 'assets/images/infografiche/L9-IngegneriMeccanica.jpg',
    percorsiCorrelati: [
      { label: 'Ingegneria Meccanica (L-9)',                         value: 'CORSO_IMEC'   },
      { label: 'Ingegneria Industriale e Sistemi Navali (L-9)',      value: 'CORSO_INAVAL' },
      { label: 'Ingegneria Elettrica (L-9)',                         value: 'CORSO_IELE'   },
    ],
  },

  {
    id: 'INAVAL',
    corso: 'Ingegneria Industriale e Sistemi Navali',
    path: 'assets/images/infografiche/L9-IngegneriIndustrialeeSistemiNavali.jpg',
    percorsiCorrelati: [
      { label: 'Ingegneria Industriale e Sistemi Navali (L-9)', value: 'CORSO_INAVAL' },
      { label: 'Ingegneria Meccanica (L-9)',                    value: 'CORSO_IMEC'   },
      { label: 'Ingegneria Gestionale (L-9)',                   value: 'CORSO_IGEST'  },
    ],
  },

  {
    id: 'IMED',
    corso: 'Ingegneria dei Sistemi Medicali',
    path: 'assets/images/infografiche/ingegneria_sistemi_medicali.jpg',
    percorsiCorrelati: [
      { label: 'Ingegneria dei Sistemi Medicali',  value: 'CORSO_IMED'  },
      { label: 'Ingegneria Meccanica (L-9)',        value: 'CORSO_IMEC'  },
      { label: 'Ingegneria Elettrica (L-9)',        value: 'CORSO_IELE'  },
    ],
  },

  // ── Aerospaziale ────────────────────────────────────────────────────────

  {
    id: 'IAERO',
    corso: 'Ingegneria dei Sistemi Aerospaziali',
    path: 'assets/images/infografiche/L8L9-IngegneriAdeiSistemiAerospaziali.jpg',
    percorsiCorrelati: [
      { label: 'Ingegneria dei Sistemi Aerospaziali',               value: 'CORSO_IAERO'  },
      { label: 'Ingegneria Meccanica (L-9)',                        value: 'CORSO_IMEC'   },
      { label: 'Ingegneria Elettronica e Tecnologie Internet (L-8)', value: 'CORSO_IETI' },
    ],
  },

  // ── Architettura / Design ───────────────────────────────────────────────

  {
    id: 'ARCH',
    corso: 'Architettura (LM-4)',
    path: 'assets/images/infografiche/LM4-Architettura.jpg',
    percorsiCorrelati: [
      { label: 'Architettura (LM-4)',           value: 'CORSO_ARCH'   },
      { label: 'Ingegneria Edile (L-23)',        value: 'CORSO_IEDILE' },
    ],
  },

  {
    id: 'LDES',
    corso: 'Design (L-4)',
    path: 'assets/images/infografiche/L4-design.jpg',
    percorsiCorrelati: [
      { label: 'Design (L-4)',                              value: 'CORSO_LDES' },
      { label: 'Ingegneria della Creatività Digitale (L-8)', value: 'CORSO_ICD' },
      { label: 'Architettura (LM-4)',                       value: 'CORSO_ARCH' },
    ],
  },

  // ── Laurea Politecnica ──────────────────────────────────────────────────

  {
    id: 'LPOL',
    corso: 'Laurea Politecnica (L-P01)',
    path: 'assets/images/infografiche/L-P01-CostruzioneGestioneAmbientaleTerritoriale.jpg',
    percorsiCorrelati: [
      { label: 'Laurea Politecnica (L-P01)',                        value: 'CORSO_LPOL'   },
      { label: "Ingegneria Informatica e dell'Automazione (L-8)",   value: 'CORSO_IIA'    },
      { label: 'Ingegneria Meccanica (L-9)',                        value: 'CORSO_IMEC'   },
    ],
  },

];
