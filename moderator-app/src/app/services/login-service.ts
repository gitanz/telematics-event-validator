import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, BehaviorSubject, finalize } from 'rxjs';
import { environment } from '../../environments/environment';
import { LocalStorage } from './local-storage';

interface LoginResponse {
  token: string
}

@Injectable({
  providedIn: 'root',
})
export class LoginService {
  private loggedInSubject = new BehaviorSubject<boolean>(false);
  public loggedIn$ = this.loggedInSubject.asObservable();

  constructor(
    private http: HttpClient,
    private localStorage: LocalStorage
  ) {
    if(this.localStorage.getLoggedIn()) {
      this.setLoggedIn();
    }
  }

  setLoggedIn() {
    this.loggedInSubject.next(true);
  }

  setLoggedOut() {
    this.loggedInSubject.next(false);
  }

  login(moderatorID: string, location: string): Observable<LoginResponse> {
    const payload = {
      moderator_id: moderatorID,
      location: location,
    };

    return this.http.post<LoginResponse>(`${environment.apiUrl}/login`, payload, {
      withCredentials: true,
    });
  }

  logout() {
    return this.http.post(`${environment.apiUrl}/logout`, {}, {
      withCredentials: true
    });
  }
}
