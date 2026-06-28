import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

// ─── Interfacce KPI ───────────────────────────────────────────────────

export interface AlmaLaureaData {
  tasso_occupazione_1_anno: number;
  retribuzione_netta_media: number;
  soddisfazione_corso: number;
  tasso_occupazione_3_anni: number | null;
  retribuzione_netta_media_3_anni: number | null;
  tasso_occupazione_5_anni: number | null;
  retribuzione_netta_media_5_anni: number | null;
  impatto_studi_titolo: string;
  impatto_studi_valore: string;
  impatto_studi_descrizione: string;
}

export interface GiudizioComparativo {
  occupazione_vs_media: 'superiore' | 'inferiore' | 'nella media';
  delta_occupazione: number;
}

export interface RecensioneData {
  parametro: string;
  valore: string;
}

export interface OpisIndicatore {
  area?: string;
  parametro: string;
  giudizi_positivi: number | null;
  giudizi_negativi: number | null;
  tipo?: string;
}

export interface OpisData {
  source?: string | null;
  anno?: string | null;
  indicatori: OpisIndicatore[];
  note?: string;
}

export interface CourseKPI {
  nome: string;
  classe: string;
  dipartimento: string;
  anno: string;
  livello: string;
  source_almalaurea: string | null;
  almalaurea: AlmaLaureaData;
  giudizio_comparativo: GiudizioComparativo;
  opis?: OpisData;
  recensioni?: RecensioneData[];
  note: string;
}

// ─── Interfaccia Raccomandazione ──────────────────────────────────────
export interface CourseRecommendation {
  corsoConsigliato: string;
  dipartimento: string;
  motivazione: string;
  puntiForza: string[];
  sbocchiLavorativi: string[];
  opportunitaInternazionali: string;
  corsiAlternativi: string[];
  consiglio: string;
  areeInteresse: { nome: string; percentuale: number }[];
  // KPI data allegati dal backend (opzionali)
  kpiData?: CourseKPI;
  courseKpiId?: string;
}

@Injectable({
  providedIn: 'root'
})
export class CourseAdvisorService {
  private apiUrl = 'http://127.0.0.1:5000/recommend';
  private analysisUrl = 'http://127.0.0.1:5000/analysis';

  constructor(private http: HttpClient) {}

  getRecommendation(
    materie: string[],
    aspirazioni: string[],
    note: string
  ): Observable<CourseRecommendation> {
    return this.http.post<CourseRecommendation>(this.apiUrl, {
      materie,
      aspirazioni,
      note
    });
  }

  getAnalysis(courseId: string): Observable<CourseKPI> {
    return this.http.get<CourseKPI>(`${this.analysisUrl}?course_id=${courseId}`);
  }
}
