import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root',
})
export class LocalStorage {
  setLoggedIn(loggedIn: boolean): void {
    if (loggedIn) {
      localStorage.setItem('loggedIn', 'true');
      return;
    }

    localStorage.removeItem('loggedIn');
  }

  getLoggedIn(): boolean {
    return localStorage.getItem('loggedIn') === 'true';
  }
}
