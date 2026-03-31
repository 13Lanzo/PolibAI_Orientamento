import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

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
}

@Injectable({
  providedIn: 'root'
})
export class CourseAdvisorService {
  private apiUrl = 'http://127.0.0.1:5000/recommend';

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
}
