import { Component, OnDestroy, OnInit } from '@angular/core';
import { MatCard, MatCardContent, MatCardHeader, MatCardTitle } from '@angular/material/card';
import { MatFormField, MatInput, MatLabel } from '@angular/material/input';
import { MatOption, MatSelect } from '@angular/material/select';
import { MatDivider } from '@angular/material/list';
import { MatButton } from '@angular/material/button';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { LoginService } from '../../services/login-service';
import { LocalStorage } from '../../services/local-storage';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-login',
  imports: [
    MatCard,
    MatCardHeader,
    MatCardTitle,
    MatCardContent,
    MatFormField,
    MatLabel,
    MatSelect,
    MatOption,
    MatInput,
    MatDivider,
    MatButton,
    ReactiveFormsModule,
  ],
  templateUrl: './login.html',
  styleUrl: './login.css',
})
export class Login implements OnInit, OnDestroy {
  loginForm = new FormGroup({
    moderatorId: new FormControl('', Validators.required),
    location: new FormControl('', Validators.required),
  });

  private loginSubscription?: Subscription;
  constructor(
    private loginService: LoginService,
    private localStorage: LocalStorage,
  ) {}
  ngOnInit(): void {}

  onLogin(event: Event): void {
    event.preventDefault();

    if (!this.loginForm.valid) {
      return;
    }

    const { moderatorId, location } = this.loginForm.value;

    if (!moderatorId || !location) {
      return;
    }

    this.loginSubscription = this.loginService.login(moderatorId, location)
      .subscribe({
        next: () => {
          this.loginService.setLoggedIn();
          this.localStorage.setLoggedIn(true);
        },
      });
  }

  ngOnDestroy() {
    if (this.loginSubscription) {
      this.loginSubscription.unsubscribe();
    }
  }
}
