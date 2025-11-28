import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
    providedIn: 'root' // Questo lo rende disponibile ovunque
})
export class ChatbotService {
    // L'indirizzo del tuo server Python (che hai acceso prima sulla porta 5000)
    private apiUrl = 'http://127.0.0.1:5000/chat';

    constructor(private http: HttpClient) { }

    sendMessage(message: string): Observable<any> {
        // Invia il messaggio al server Flask
        return this.http.post<any>(this.apiUrl, { message: message });
    }
}