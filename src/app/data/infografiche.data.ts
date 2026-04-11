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
  {
    id: 'IIA',
    corso: "Ingegneria Informatica e dell'Automazione",
    path: 'assets/infografiche/ingegneria_informatica_automazione.jpg',
    percorsiCorrelati: [
      { label: "Ingegneria Informatica e dell'Automazione (L-8)", value: 'CORSO_IIA' },
      { label: 'Ingegneria della Creatività Digitale (L-8)',      value: 'CORSO_ICD'  },
      { label: 'Ingegneria Elettronica e Tecnologie Internet (L-8)', value: 'CORSO_IETI' },
    ],
  },
  {
    id: 'ICD',
    corso: 'Ingegneria della Creatività Digitale',
    path: 'assets/infografiche/ingegneria_creativita_digitale.jpg',
    percorsiCorrelati: [
      { label: 'Ingegneria della Creatività Digitale (L-8)',      value: 'CORSO_ICD'  },
      { label: "Ingegneria Informatica e dell'Automazione (L-8)", value: 'CORSO_IIA'  },
      { label: 'Ingegneria Elettronica e Tecnologie Internet (L-8)', value: 'CORSO_IETI' },
    ],
  },
  {
    id: 'IETI',
    corso: 'Ingegneria Elettronica e Tecnologie Internet',
    path: 'assets/infografiche/L8-IngegneriaElettronicaeTecnologieInternet.png',
    percorsiCorrelati: [
      { label: 'Ingegneria Elettronica e Tecnologie Internet (L-8)', value: 'CORSO_IETI' },
      { label: "Ingegneria Informatica e dell'Automazione (L-8)", value: 'CORSO_IIA'  },
      { label: 'Ingegneria della Creatività Digitale (L-8)',      value: 'CORSO_ICD'  },
    ],
  },
  {
    id: 'ICIVAMB',
    corso: 'Ingegneria Civile e Ambientale',
    path: 'assets/infografiche/L7-ingegneriaCivileAmbientale.png',
    percorsiCorrelati: [
      { label: 'Ingegneria Civile e Ambientale (L-7)',  value: 'CORSO_ICIVAMB' },
      { label: 'Ingegneria Edile (L-23)',               value: 'CORSO_IEDILE'  },
    ],
  },
  {
    id: 'IEDILE',
    corso: 'Ingegneria Edile',
    path: 'assets/infografiche/ingegneria_edile.jpg',
    percorsiCorrelati: [
      { label: 'Ingegneria Edile (L-23)',               value: 'CORSO_IEDILE'  },
      { label: 'Ingegneria Civile e Ambientale (L-7)',  value: 'CORSO_ICIVAMB' },
    ],
  },
  {
    id: 'IELE',
    corso: 'Ingegneria Elettrica',
    path: 'assets/infografiche/L9-IngegneriaElettrica.png',
    percorsiCorrelati: [
      { label: 'Ingegneria Elettrica (L-9)',            value: 'CORSO_IELE'   },
      { label: 'Ingegneria Meccanica (L-9)',            value: 'CORSO_IMEC'   },
      { label: 'Ingegneria Gestionale (L-9)',           value: 'CORSO_IGEST'  },
    ],
  },
  {
    id: 'IGEST',
    corso: 'Ingegneria Gestionale',
    path: 'assets/infografiche/L9-IngegneriaGestionale.png',
    percorsiCorrelati: [
      { label: 'Ingegneria Gestionale (L-9)',           value: 'CORSO_IGEST'  },
      { label: 'Ingegneria Meccanica (L-9)',            value: 'CORSO_IMEC'   },
      { label: 'Ingegneria Elettrica (L-9)',            value: 'CORSO_IELE'   },
    ],
  },
  {
    id: 'IMEC',
    corso: 'Ingegneria Meccanica',
    path: 'assets/infografiche/L9-IngegneriaMeccanica.png',
    percorsiCorrelati: [
      { label: 'Ingegneria Meccanica (L-9)',                         value: 'CORSO_IMEC'   },
      { label: 'Ingegneria Industriale e Sistemi Navali (L-9)',  value: 'CORSO_INAVAL' },
      { label: 'Ingegneria Elettrica (L-9)',                         value: 'CORSO_IELE'   },
    ],
  },
  {
    id: 'INAVAL',
    corso: 'Ingegneria Industriale e Sistemi Navali',
    path: 'assets/infografiche/L9-IngegneriaIndustrialeeSistemiNavali.png',
    percorsiCorrelati: [
      { label: 'Ingegneria Industriale e Sistemi Navali (L-9)', value: 'CORSO_INAVAL' },
      { label: 'Ingegneria Meccanica (L-9)',                        value: 'CORSO_IMEC'   },
      { label: 'Ingegneria Gestionale (L-9)',                       value: 'CORSO_IGEST'  },
    ],
  },
  {
    id: 'IMED',
    corso: 'Ingegneria dei Sistemi Medicali',
    path: 'assets/infografiche/ingegneria_sistemi_medicali.jpg',
    percorsiCorrelati: [
      { label: 'Ingegneria dei Sistemi Medicali',  value: 'CORSO_IMED'  },
      { label: 'Ingegneria Meccanica (L-9)',        value: 'CORSO_IMEC'  },
      { label: 'Ingegneria Elettrica (L-9)',        value: 'CORSO_IELE'  },
    ],
  },
  {
    id: 'IAERO',
    corso: 'Ingegneria dei Sistemi Aerospaziali',
    path: 'assets/infografiche/L8L9-IngegneriadeiSistemiAereospaziali.png',
    percorsiCorrelati: [
      { label: 'Ingegneria dei Sistemi Aerospaziali', value: 'CORSO_IAERO'  },
      { label: 'Ingegneria Meccanica (L-9)',           value: 'CORSO_IMEC'   },
      { label: 'Ingegneria Elettronica e Tecnologie Internet (L-8)', value: 'CORSO_IETI' },
    ],
  },
  {
    id: 'ARCH',
    corso: 'Architettura (LM-4)',
    path: 'assets/infografiche/LM4-Architettura.png',
    percorsiCorrelati: [
      { label: 'Architettura (LM-4)',           value: 'CORSO_ARCH'   },
      { label: 'Ingegneria Edile (L-23)',        value: 'CORSO_IEDILE' },
    ],
  },
  {
    id: 'LDES',
    corso: 'Design (L-4)',
    path: 'assets/infografiche/L4-design.png',
    percorsiCorrelati: [
      { label: 'Design (L-4)',                              value: 'CORSO_LDES' },
      { label: 'Ingegneria della Creatività Digitale (L-8)', value: 'CORSO_ICD' },
      { label: 'Architettura (LM-4)',                       value: 'CORSO_ARCH' },
    ],
  },
  {
    id: 'LPOL',
    corso: 'Laurea Politecnica (L-P01)',
    path: 'assets/infografiche/L-P01.png',
    percorsiCorrelati: [
      { label: 'Laurea Politecnica (L-P01)',                        value: 'CORSO_LPOL'   },
      { label: "Ingegneria Informatica e dell'Automazione (L-8)",   value: 'CORSO_IIA'    },
      { label: 'Ingegneria Meccanica (L-9)',                        value: 'CORSO_IMEC'   },
    ],
  },
];
