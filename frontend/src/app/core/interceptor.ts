import { HttpErrorResponse, HttpHandlerFn, HttpInterceptorFn, HttpRequest } from "@angular/common/http";
import { inject } from "@angular/core";
import { environment } from "@shared/environments/environment";
import { AuthService } from "@shared/services/auth.service";
import { throwError } from "rxjs/internal/observable/throwError";
import { catchError } from "rxjs/internal/operators/catchError";
import { switchMap } from "rxjs/internal/operators/switchMap";

export const Interceptor: HttpInterceptorFn = (request: HttpRequest<any>, next: HttpHandlerFn) => {
    const authService: AuthService = inject(AuthService);

    let newRequest: HttpRequest<any> = request;

    if (request.url.startsWith(environment.serverURL)) {
        newRequest = request.clone({ withCredentials: true });
    }

    return next(newRequest).pipe(
        catchError((error: HttpErrorResponse) => {
            if (error.status == 401) {
                return authService.refreshToken().pipe(
                    switchMap(() => next(newRequest)),
                    catchError((refreshError) => {
                        authService.user.set(null);
                        return throwError(() => refreshError);
                    }),
                );
            }

            return throwError(() => error);
        }),
    );
};
