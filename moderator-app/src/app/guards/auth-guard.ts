import { CanActivateFn, Router } from '@angular/router';
import { inject } from '@angular/core';
import { LocalStorage } from '../services/local-storage';


export const authGuard: CanActivateFn = (route, state) => {
  const router = inject(Router);
  const localStorageService = inject(LocalStorage);
  console.log(localStorageService.getLoggedIn());
  if (!localStorageService.getLoggedIn()) {
    router.navigate(['login']);
    return false;
  }
  return true;
};
