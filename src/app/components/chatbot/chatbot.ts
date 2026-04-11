import { Component, signal, ViewChild, ElementRef, AfterViewChecked } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ChatbotService } from './chatbot.service';
import { marked } from 'marked';
import DOMPurify from 'dompurify';
import { INFOGRAFICHE } from '../../data/infografiche.data';

interface QuickOption {
    label: string;
    value: string;
}

interface Message {
    text?: string;
    htmlText?: string;
    sender: 'user' | 'bot';
    timestamp: Date;
    type: 'text' | 'map' | 'options' | 'image';
    mapUrl?: string;
    mapTitle?: string;
    options?: QuickOption[];
    infograficaId?: string;
}

@Component({
    selector: 'app-chatbot',
    standalone: true,
    imports: [CommonModule, FormsModule],
    templateUrl: './chatbot.html',
    styleUrl: './chatbot.css'
})
export class Chatbot implements AfterViewChecked {
    @ViewChild('scrollContainer') private scrollContainer!: ElementRef;
    
    currentInput = signal('');
    isLoading = signal(false);
    messages = signal<Message[]>([]);

    constructor(private chatbotService: ChatbotService) { }

    ngAfterViewChecked() {
        this.scrollToBottom();
    }

    private scrollToBottom(): void {
        try {
            if (this.scrollContainer) {
                this.scrollContainer.nativeElement.scrollTop = this.scrollContainer.nativeElement.scrollHeight;
            }
        } catch(err) { }
    }

    sendSuggestion(text: string) {
        this.currentInput.set(text);
        this.sendMessage();
    }

    sendMessage() {
        const text = this.currentInput().trim();
        if (!text) return;

        this.addMessageToChat({
            text,
            sender: 'user',
            timestamp: new Date(),
            type: 'text'
        });

        this.currentInput.set('');
        this.callBackend(text);
    }

    sendOption(value: string, label: string) {
        this.addMessageToChat({
            text: `Ho scelto: ${label}`,
            sender: 'user',
            timestamp: new Date(),
            type: 'text'
        });
        this.callBackend(value);
    }

    openMap(url: string | undefined) {
        if (url) window.open(url, '_blank');
    }

    loadInfographic(id: string) {
        const info = INFOGRAFICHE.find(i => i.id === id);
        if (info) {
            this.addMessageToChat({
                sender: 'user',
                timestamp: new Date(),
                type: 'text',
                text: `Mostra l'infografica: ${info.corso}`
            });
            this.addMessageToChat({
                sender: 'bot',
                timestamp: new Date(),
                type: 'image',
                text: `Ecco l'infografica per **${info.corso}**.`,
                mapUrl: info.path,
                options: info.percorsiCorrelati
            });
        }
    }

    resetChat() {
        this.messages.set([]);
        this.currentInput.set('');
        this.isLoading.set(false);
    }

    private callBackend(msgText: string) {
        this.isLoading.set(true);

        this.chatbotService.sendMessage(msgText).subscribe({
            next: (response: any) => {
                this.isLoading.set(false);
                // Parse the markdown string
                let parsedHTML = '';
                if (response.response) {
                    try {
                        // marked.parse returns a string synchronously when run this way
                        const rawHtml = marked.parse(response.response) as string;
                        parsedHTML = DOMPurify.sanitize(rawHtml);
                    } catch (e) {
                        parsedHTML = response.response; // Fallback
                    }
                }

                const botMsg: Message = {
                    sender: 'bot',
                    timestamp: new Date(),
                    type: response.type || 'text',
                    text: response.response,
                    htmlText: parsedHTML,
                    mapUrl: response.mapUrl,
                    mapTitle: response.mapTitle,
                    options: response.options,
                    infograficaId: response.infograficaId
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

    private addMessageToChat(msg: Message) {
        this.messages.update(msgs => [...msgs, msg]);
    }
}