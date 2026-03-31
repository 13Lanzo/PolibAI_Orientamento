import { Component, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { CourseAdvisorService, CourseRecommendation } from './course-advisor.service';

interface PolibaCourse {
  id: number;
  nome: string;
  tipo: string;
  dipartimento: string;
  classe: string;
  en: boolean;
  nuovo?: boolean;
  aree: string[];
}

const POLIBA_COURSES: PolibaCourse[] = [
  { id: 1, nome: "Architettura", tipo: "Magistrale a Ciclo Unico (5 anni)", dipartimento: "ARCOD", classe: "LM4", en: false, aree: ["progettazione", "urbanistica", "restauro", "arte", "territorio", "patrimonio"] },
  { id: 2, nome: "Architecture Sciences for Heritage", tipo: "Triennale", dipartimento: "ARCOD", classe: "L17", en: true, nuovo: true, aree: ["architettura", "patrimonio culturale", "restauro", "internazionale"] },
  { id: 3, nome: "Design", tipo: "Triennale", dipartimento: "ARCOD", classe: "L4", en: false, aree: ["design", "prodotto industriale", "creatività", "comunicazione visiva", "artigianato"] },
  { id: 4, nome: "Industrial Design", tipo: "Magistrale", dipartimento: "ARCOD", classe: "LM12", en: true, aree: ["design avanzato", "prodotto", "internazionale", "UX"] },
  { id: 5, nome: "Costruzioni e Gestione Ambientale e Territoriale", tipo: "Triennale Professionalizzante", dipartimento: "DICATECh", classe: "L-P01", en: false, aree: ["costruzioni", "geometria", "territorio", "ambiente", "cantiere", "catasto"] },
  { id: 6, nome: "Ingegneria Civile e Ambientale", tipo: "Triennale", dipartimento: "DICATECh", classe: "L7", en: false, aree: ["strutture", "idraulica", "ambiente", "territorio", "infrastrutture", "costruzioni"] },
  { id: 7, nome: "Ingegneria Edile", tipo: "Triennale", dipartimento: "DICATECh", classe: "L7", en: false, aree: ["edilizia", "costruzioni", "strutture", "cantiere", "materiali"] },
  { id: 8, nome: "Ingegneria della Mobilità Sostenibile", tipo: "Magistrale", dipartimento: "DICATECh", classe: "LM26", en: false, aree: ["trasporti", "mobilità", "sostenibilità", "big data", "sicurezza"] },
  { id: 9, nome: "Ingegneria Gestionale", tipo: "Triennale", dipartimento: "DMMM", classe: "L9", en: false, aree: ["management", "organizzazione", "logistica", "economia", "processi aziendali", "lean"] },
  { id: 10, nome: "Ingegneria Meccanica", tipo: "Triennale", dipartimento: "DMMM", classe: "L9", en: false, aree: ["meccanica", "progettazione meccanica", "automazione", "produzione", "termodinamica"] },
  { id: 11, nome: "Management Engineering for Innovation", tipo: "Triennale", dipartimento: "DMMM", classe: "L9", en: true, nuovo: true, aree: ["management", "innovazione", "digitale", "AI", "internazionale", "startup", "trasformazione digitale"] },
  { id: 12, nome: "Ingegneria Industriale e dei Sistemi Navali", tipo: "Triennale", dipartimento: "DMMM", classe: "L9", en: false, aree: ["navale", "industriale", "produzione", "impianti"] },
  { id: 13, nome: "Ingegneria Elettrica", tipo: "Triennale", dipartimento: "DEI", classe: "L9", en: false, aree: ["elettrica", "energia", "reti elettriche", "impianti elettrici", "rinnovabili"] },
  { id: 14, nome: "Ingegneria dei Sistemi Aerospaziali", tipo: "Triennale", dipartimento: "DEI", classe: "L8", en: false, aree: ["aerospazio", "aeronautica", "velivoli", "satelliti", "difesa"] },
  { id: 15, nome: "Ingegneria dei Sistemi Medicali", tipo: "Triennale", dipartimento: "DEI", classe: "L8", en: false, aree: ["biomedica", "medicina", "dispositivi medici", "sanità", "salute"] },
  { id: 16, nome: "Energy Engineering", tipo: "Magistrale", dipartimento: "DEI", classe: "LM30", en: true, aree: ["energia", "rinnovabili", "sostenibilità", "internazionale", "green"] },
  { id: 17, nome: "Automation and Robotics Engineering", tipo: "Magistrale", dipartimento: "DIEI", classe: "LM32", en: true, aree: ["robotica", "automazione", "AI", "controllo", "industria 4.0"] },
  { id: 18, nome: "Computer Engineering", tipo: "Magistrale", dipartimento: "DIEI", classe: "LM32", en: true, aree: ["informatica", "software", "AI", "cloud", "cybersecurity", "programmazione"] },
  { id: 19, nome: "Electronics Engineering", tipo: "Magistrale", dipartimento: "DIEI", classe: "LM29", en: true, aree: ["elettronica", "circuiti", "embedded", "IoT", "segnali"] },
  { id: 20, nome: "Telecommunication and Internet Technologies Engineering", tipo: "Magistrale", dipartimento: "DIEI", classe: "LM27", en: true, aree: ["telecomunicazioni", "reti", "internet", "5G", "wireless"] },
  { id: 21, nome: "Ingegneria Informatica e dell'Automazione", tipo: "Triennale", dipartimento: "DIEI", classe: "L8", en: false, aree: ["informatica", "programmazione", "reti", "sistemi", "automazione"] },
  { id: 22, nome: "Ingegneria Elettronica e delle Tecnologie Internet", tipo: "Triennale", dipartimento: "DIEI", classe: "L8", en: false, aree: ["elettronica", "internet", "reti", "telecomunicazioni", "IoT"] },
  { id: 23, nome: "Ingegneria della Creatività Digitale", tipo: "Triennale", dipartimento: "DIEI", classe: "L8", en: false, nuovo: true, aree: ["digitale", "creatività", "media", "app", "UX", "gaming"] },
];

const DEPT_COLORS: Record<string, { bg: string; text: string; border: string }> = {
  ARCOD: { bg: "#fff0f2", text: "#C8102E", border: "#f7c4cc" },
  DICATECh: { bg: "#e1f5ee", text: "#0f6e56", border: "#9fe1cb" },
  DMMM: { bg: "#e6f1fb", text: "#185fa5", border: "#b5d4f4" },
  DEI: { bg: "#faeeda", text: "#854f0b", border: "#fac775" },
  DIEI: { bg: "#fbeaf0", text: "#993556", border: "#f4c0d1" },
};

const INTEREST_SUGGESTIONS = [
  "Matematica", "Fisica", "Informatica", "Arte", "Disegno", "Chimica",
  "Storia", "Economia", "Biologia", "Lingue straniere", "Musica",
  "Sport", "Tecnologia", "Ambiente", "Architettura", "Elettronica",
  "Robotica", "Design", "Meccanica", "Programmazione"
];

const JOB_SUGGESTIONS = [
  "Ingegnere informatico", "Architetto", "Designer di prodotto", "Data scientist",
  "Manager aziendale", "Ingegnere aerospaziale", "Ricercatore", "Startup founder",
  "Ingegnere ambientale", "Robotics engineer", "Ingegnere biomedico", "Project manager",
  "UX Designer", "Energy manager", "Ingegnere civile"
];

@Component({
  selector: 'app-course-advisor',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './course-advisor.html',
  styleUrl: './course-advisor.css'
})
export class CourseAdvisor {
  // Step control
  step = signal<'intro' | 'form' | 'loading' | 'result'>('intro');

  // Form data
  materie = signal<string[]>([]);
  aspirazioni = signal<string[]>([]);
  materiInput = signal('');
  aspInput = signal('');
  note = signal('');

  // Result
  result = signal<(CourseRecommendation & { courseData?: PolibaCourse }) | null>(null);
  error = signal<string | null>(null);
  loadingProgress = signal(0);

  // Chart animation
  chartAnimated = signal(false);

  // Expose constants to template
  interestSuggestions = INTEREST_SUGGESTIONS;
  jobSuggestions = JOB_SUGGESTIONS;

  // Computed: filtered suggestions
  filteredInterests = computed(() =>
    INTEREST_SUGGESTIONS.filter(s => !this.materie().includes(s)).slice(0, 10)
  );
  filteredJobs = computed(() =>
    JOB_SUGGESTIONS.filter(s => !this.aspirazioni().includes(s)).slice(0, 8)
  );
  canSubmit = computed(() => this.materie().length > 0 || this.aspirazioni().length > 0);

  constructor(private advisorService: CourseAdvisorService) {}

  // --- Tag management ---
  addMateria() {
    const v = this.materiInput().trim();
    if (v && !this.materie().includes(v)) {
      this.materie.update(list => [...list, v]);
    }
    this.materiInput.set('');
  }

  addMateriaFromSuggestion(val: string) {
    if (!this.materie().includes(val)) {
      this.materie.update(list => [...list, val]);
    }
  }

  removeMateria(val: string) {
    this.materie.update(list => list.filter(x => x !== val));
  }

  addAspirazione() {
    const v = this.aspInput().trim();
    if (v && !this.aspirazioni().includes(v)) {
      this.aspirazioni.update(list => [...list, v]);
    }
    this.aspInput.set('');
  }

  addAspirazioneFromSuggestion(val: string) {
    if (!this.aspirazioni().includes(val)) {
      this.aspirazioni.update(list => [...list, val]);
    }
  }

  removeAspirazione(val: string) {
    this.aspirazioni.update(list => list.filter(x => x !== val));
  }

  onMateriaKeydown(event: KeyboardEvent) {
    if (event.key === 'Enter') {
      event.preventDefault();
      this.addMateria();
    }
  }

  onAspKeydown(event: KeyboardEvent) {
    if (event.key === 'Enter') {
      event.preventDefault();
      this.addAspirazione();
    }
  }

  // --- Navigation ---
  goToForm() { this.step.set('form'); }
  goToIntro() { this.reset(); }

  // --- AI Recommendation ---
  getRecommendation() {
    if (!this.canSubmit()) return;
    this.step.set('loading');
    this.error.set(null);
    this.loadingProgress.set(0);
    this.chartAnimated.set(false);

    // Simulate progress
    const interval = setInterval(() => {
      this.loadingProgress.update(p => {
        if (p >= 90) { clearInterval(interval); return 90; }
        return p + Math.random() * 15;
      });
    }, 300);

    this.advisorService.getRecommendation(
      this.materie(),
      this.aspirazioni(),
      this.note()
    ).subscribe({
      next: (response) => {
        clearInterval(interval);
        this.loadingProgress.set(100);
        const courseData = POLIBA_COURSES.find(c => c.nome === response.corsoConsigliato);
        this.result.set({ ...response, courseData });
        setTimeout(() => {
          this.step.set('result');
          // Trigger chart animation after render
          setTimeout(() => this.chartAnimated.set(true), 100);
        }, 400);
      },
      error: (err) => {
        clearInterval(interval);
        console.error('Errore raccomandazione:', err);
        this.error.set('Si è verificato un errore nella comunicazione con il server. Riprova.');
        this.step.set('form');
      }
    });
  }

  reset() {
    this.step.set('intro');
    this.materie.set([]);
    this.aspirazioni.set([]);
    this.note.set('');
    this.result.set(null);
    this.error.set(null);
    this.loadingProgress.set(0);
    this.chartAnimated.set(false);
  }

  // --- Helpers for template ---
  getDeptColor(dept: string) {
    return DEPT_COLORS[dept] || { bg: '#f5f5f5', text: '#333', border: '#ddd' };
  }

  getLoadingPercent(): number {
    return Math.min(95, Math.round(this.loadingProgress()));
  }

  // --- Radar Chart SVG ---
  getRadarPoints(aree: { nome: string; percentuale: number }[], animated: boolean): string {
    if (!aree || aree.length === 0) return '';
    const cx = 150, cy = 150, maxR = 120;
    const n = aree.length;
    return aree.map((area, i) => {
      const angle = (Math.PI * 2 * i) / n - Math.PI / 2;
      const r = animated ? (area.percentuale / 100) * maxR : 0;
      const x = cx + r * Math.cos(angle);
      const y = cy + r * Math.sin(angle);
      return `${x},${y}`;
    }).join(' ');
  }

  getRadarGridPoints(level: number): string {
    const cx = 150, cy = 150, maxR = 120;
    const n = this.result()?.areeInteresse?.length || 6;
    const r = (level / 100) * maxR;
    const points: string[] = [];
    for (let i = 0; i < n; i++) {
      const angle = (Math.PI * 2 * i) / n - Math.PI / 2;
      points.push(`${cx + r * Math.cos(angle)},${cy + r * Math.sin(angle)}`);
    }
    return points.join(' ');
  }

  getRadarAxisEndX(index: number): number {
    const cx = 150, maxR = 120;
    const n = this.result()?.areeInteresse?.length || 6;
    const angle = (Math.PI * 2 * index) / n - Math.PI / 2;
    return cx + maxR * Math.cos(angle);
  }

  getRadarAxisEndY(index: number): number {
    const cy = 150, maxR = 120;
    const n = this.result()?.areeInteresse?.length || 6;
    const angle = (Math.PI * 2 * index) / n - Math.PI / 2;
    return cy + maxR * Math.sin(angle);
  }

  getRadarLabelX(index: number): number {
    const cx = 150, maxR = 140;
    const n = this.result()?.areeInteresse?.length || 6;
    const angle = (Math.PI * 2 * index) / n - Math.PI / 2;
    return cx + maxR * Math.cos(angle);
  }

  getRadarLabelY(index: number): number {
    const cy = 150, maxR = 140;
    const n = this.result()?.areeInteresse?.length || 6;
    const angle = (Math.PI * 2 * index) / n - Math.PI / 2;
    return cy + maxR * Math.sin(angle);
  }

  openPoliba() {
    window.open('https://www.poliba.it', '_blank');
  }
}
