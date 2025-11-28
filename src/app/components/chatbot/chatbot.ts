import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ChatbotService } from './chatbot.service'; // <--- Importa il servizio

interface Message {
    text: string;
    sender: 'user' | 'bot';
    timestamp: Date;
}

@Component({
    selector: 'app-chatbot',
    standalone: true,
    imports: [CommonModule, FormsModule],
    templateUrl: './chatbot.html',
    styleUrl: './chatbot.css' // Attenzione: in Angular moderno è 'styleUrl' (singolare) o 'styleUrls' (array)
})
export class Chatbot {
    isOpen = signal(false);
    currentInput = signal('');
    isLoading = signal(false); // <--- Utile per mostrare "sta scrivendo..."

    messages = signal<Message[]>([
        { text: 'Ciao! Sono l\'assistente virtuale del Poliba. Come posso aiutarti?', sender: 'bot', timestamp: new Date() }
    ]);

    // Iniettiamo il servizio nel costruttore
    constructor(private chatbotService: ChatbotService) { }

    toggleChat() {
        this.isOpen.set(!this.isOpen());
    }

    sendMessage() {
        const text = this.currentInput().trim();
        if (!text) return;

        // 1. Aggiungi subito il messaggio dell'utente alla lista
        this.messages.update(msgs => [...msgs, { text, sender: 'user', timestamp: new Date() }]);
        this.currentInput.set(''); // Pulisci input
        this.isLoading.set(true);  // Attiva caricamento

        // 2. Chiama il server Python tramite il Service
        this.chatbotService.sendMessage(text).subscribe({
            next: (response) => {
                // 3. Quando arriva la risposta da Python
                this.messages.update(msgs => [...msgs, {
                    text: response.response, // Python ci restituisce un JSON { "response": "..." }
                    sender: 'bot',
                    timestamp: new Date()
                }]);
                this.isLoading.set(false); // Spegni caricamento
            },
            error: (error) => {
                console.error('Errore backend:', error);
                // Messaggio di errore in chat
                this.messages.update(msgs => [...msgs, {
                    text: 'Mi dispiace, non riesco a contattare il server del Poliba in questo momento.',
                    sender: 'bot',
                    timestamp: new Date()
                }]);
                this.isLoading.set(false);
            }
        });
    }
}