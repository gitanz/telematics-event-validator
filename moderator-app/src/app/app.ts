import { Component, signal } from '@angular/core';
import { Router, RouterOutlet } from '@angular/router';
import { MatToolbar } from '@angular/material/toolbar';
import { MatProgressBar } from '@angular/material/progress-bar';
import { LoginService } from './services/login-service';
import { AppService } from './services/app-service';
import { AsyncPipe } from '@angular/common';
import { MatButton, MatIconButton } from '@angular/material/button';
import { LocalStorage } from './services/local-storage';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, MatToolbar, MatProgressBar, AsyncPipe, MatButton],
  templateUrl: './app.html',
  styleUrl: './app.css',
})
export class App {
  protected readonly title = signal('moderator-app');
  constructor(
    public appService: AppService,
    private loginService: LoginService,
    private localStorage: LocalStorage,
    private router: Router,
  ) {
    this.loginService.loggedIn$.subscribe({
      next: (loggedIn) => {
        if (!loggedIn) {
          this.router.navigate(['login']);
          return;
        }

        this.router.navigate(['']);
      },
    });
  }

  logout() {
    this.loginService.logout().subscribe({
      next: () => {
        this.loginService.setLoggedOut();
        this.localStorage.setLoggedIn(false);
      }
    })
      .unsubscribe();
  }
}
