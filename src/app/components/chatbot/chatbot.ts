import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ChatbotService } from './chatbot.service';

// --- NUOVA INTERFACCIA PER I BOTTONI ---
interface QuickOption {
    label: string;
    value: string;
}

// --- INTERFACCIA MESSAGGIO AGGIORNATA ---
interface Message {
    text?: string; // Reso opzionale per gestire solo mappe
    sender: 'user' | 'bot';
    timestamp: Date;

    // Campi aggiunti per la logica Mappe/Opzioni
    type: 'text' | 'map' | 'options';
    mapUrl?: string;
    mapTitle?: string;
    options?: QuickOption[];
}

@Component({
    selector: 'app-chatbot',
    standalone: true,
    imports: [CommonModule, FormsModule],
    templateUrl: './chatbot.html',
    styleUrl: './chatbot.css'
})
export class Chatbot {
    isOpen = signal(false);
    currentInput = signal('');
    isLoading = signal(false);

    messages = signal<Message[]>([
        {
            text: 'Ciao! Sono l\'assistente virtuale del Poliba. Posso indicarti aule e percorsi. Come posso aiutarti?',
            sender: 'bot',
            timestamp: new Date(),
            type: 'text' // Tipo default
        }
    ]);

    constructor(private chatbotService: ChatbotService) { }

    toggleChat() {
        this.isOpen.set(!this.isOpen());
    }

    // 1. INVIO MESSAGGIO TESTUALE (Dall'input)
    sendMessage() {
        const text = this.currentInput().trim();
        if (!text) return;

        // Aggiungi messaggio utente
        this.addMessageToChat({
            text,
            sender: 'user',
            timestamp: new Date(),
            type: 'text'
        });

        this.currentInput.set('');
        this.callBackend(text);
    }

    // 2. INVIO SCELTA DA BOTTONE 
    sendOption(value: string, label: string) {
        // Mostriamo visivamente cosa ha scelto l'utente
        this.addMessageToChat({
            text: `Ho scelto: ${label}`,
            sender: 'user',
            timestamp: new Date(),
            type: 'text'
        });

        // Mandiamo il valore tecnico al backend
        this.callBackend(value);
    }

    // 3. APERTURA MAPPA 
    openMap(url: string | undefined) {
        if (url) window.open(url, '_blank');
    }

    // --- LOGICA COMUNE CHIAMATA SERVER ---
    private callBackend(msgText: string) {
        this.isLoading.set(true);

        this.chatbotService.sendMessage(msgText).subscribe({
            next: (response: any) => {
                this.isLoading.set(false);

                // Creiamo il messaggio bot basandoci sul "type" ricevuto dal Python
                const botMsg: Message = {
                    sender: 'bot',
                    timestamp: new Date(),
                    type: response.type || 'text', // Se manca, default a text
                    text: response.response,       // Il testo descrittivo

                    // Mappiamo i campi specifici dal JSON Python
                    mapUrl: response.mapUrl,
                    mapTitle: response.mapTitle,
                    options: response.options
                };

                this.addMessageToChat(botMsg);
            },
            error: (error) => {
                console.error('Errore backend:', error);
                this.isLoading.set(false);
                this.addMessageToChat({
                    text: 'Mi dispiace, non riesco a contattare il server del Poliba in questo momento.',
                    sender: 'bot',
                    timestamp: new Date(),
                    type: 'text'
                });
            }
        });
    }

    // Helper per aggiornare il signal in modo pulito
    private addMessageToChat(msg: Message) {
        this.messages.update(msgs => [...msgs, msg]);
    }
}