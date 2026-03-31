import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: '',
    loadComponent: () => import('./components/chatbot/chatbot').then(m => m.Chatbot)
  },
  {
    path: 'advisor',
    loadComponent: () => import('./components/course-advisor/course-advisor').then(m => m.CourseAdvisor)
  }
];
