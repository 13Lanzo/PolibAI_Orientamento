import { Component, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { Chatbot } from './components/chatbot/chatbot';

import { Header } from './components/header/header';
import { Navbar } from './components/navbar/navbar';
import { Hero } from './components/hero/hero';
import { Footer } from './components/footer/footer';
import { PrimoPiano } from './components/primo-piano/primo-piano';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, Header, Navbar, Hero, Footer, PrimoPiano, Chatbot],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  protected readonly title = signal('progettoFrontend');
}
