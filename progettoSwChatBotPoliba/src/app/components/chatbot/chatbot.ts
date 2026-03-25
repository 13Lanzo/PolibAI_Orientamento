import { Component, signal, ViewChild, ElementRef, AfterViewChecked } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ChatbotService } from './chatbot.service';
import { marked } from 'marked';
import DOMPurify from 'dompurify';

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
        if (value.startsWith('MOSTRA_INFO_')) {
            const courseName = value.replace('MOSTRA_INFO_', '');
            this.handleShowInfographic(courseName);
            return;
        }

        this.addMessageToChat({
            text: `Ho scelto: ${label}`,
            sender: 'user',
            timestamp: new Date(),
            type: 'text'
        });
        this.callBackend(value);
    }

    handleShowInfographic(courseName: string) {
        // Map common courses to their static filenames
        const fileNameMap: { [key: string]: string } = {
            'Ingegneria Informatica': 'ingegneria_informatica.jpg',
            'Ingegneria Meccanica': 'ingegneria_meccanica.jpg',
            'Ingegneria Gestionale': 'ingegneria_gestionale.jpg',
            'Ingegneria Civile': 'ingegneria_civile.jpg',
            'Ingegneria Edile': 'ingegneria_edile.jpg',
            'Architettura': 'architettura.jpg',
            'Design': 'design.jpg'
        };

        const fileName = fileNameMap[courseName] || 'default.jpg';
        const imgUrl = `assets/infografiche/${fileName}`;

        this.addMessageToChat({
            sender: 'bot',
            timestamp: new Date(),
            type: 'image',
            mapUrl: imgUrl,
            text: `Ecco un'infografica riassuntiva per il corso di laurea in **${courseName}**.`
        });
    }

    openMap(url: string | undefined) {
        if (url) window.open(url, '_blank');
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

                let injectedOptions = response.options || [];
                const txt = response.response?.toLowerCase() || '';
                
                // Auto-detect degree course to suggest infographic
                if (!injectedOptions.some((o: QuickOption) => o.value.startsWith('MOSTRA_INFO'))) {
                    const courses = ['Ingegneria Informatica', 'Ingegneria Meccanica', 'Ingegneria Gestionale', 'Ingegneria Civile', 'Ingegneria Edile', 'Architettura', 'Design'];
                    for (const c of courses) {
                        if (txt.includes(c.toLowerCase())) {
                            injectedOptions.push({
                                label: `🖼️ Mostra Infografica ${c}`,
                                value: `MOSTRA_INFO_${c}`
                            });
                            break; // Add only one option max
                        }
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
                    options: injectedOptions
                };
                this.addMessageToChat(botMsg);
            },
            error: (error: any) => {
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
        this.messages.update((msgs: Message[]) => [...msgs, msg]);
    }
}