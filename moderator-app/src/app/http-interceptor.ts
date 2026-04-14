import { HttpEvent, HttpHandlerFn, HttpRequest } from '@angular/common/http';
import { catchError, EMPTY, finalize, Observable, throwError } from 'rxjs';
import { AppService } from './services/app-service';
import { inject } from '@angular/core';
import { Router } from '@angular/router';

export function httpInterceptor(
  req: HttpRequest<unknown>,
  next: HttpHandlerFn,
): Observable<HttpEvent<unknown>> {
  const appService = inject(AppService);
  const router = inject(Router);
  appService.showLoading();
  const authReq = req.clone({ withCredentials: true });

  return next(authReq).pipe(
    catchError((err: any) => {
      if (err.status === 401) {
        router.navigate(['login']);
        return EMPTY;
      }
      return throwError(() => err);
    }),
    finalize(() => appService.hideLoading())
  );
}
