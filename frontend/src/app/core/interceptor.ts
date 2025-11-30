import { HttpErrorResponse, HttpHandlerFn, HttpInterceptorFn, HttpRequest } from "@angular/common/http";
import { inject } from "@angular/core";
import { Router } from "@angular/router";
import { environment } from "@shared/environments/environment";
import { AuthService } from "@shared/services/auth.service";
import { throwError } from "rxjs/internal/observable/throwError";
import { catchError } from "rxjs/internal/operators/catchError";
import { switchMap } from "rxjs/internal/operators/switchMap";

/**
 * Get CSRF token from cookies
 */
function getCsrfToken(): string | null {
    const name = "csrftoken";
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) {
        return parts.pop()?.split(";").shift() || null;
    }
    return null;
}

export const Interceptor: HttpInterceptorFn = (request: HttpRequest<any>, next: HttpHandlerFn) => {
    const authService: AuthService = inject(AuthService);
    const router: Router = inject(Router);

    // Log outgoing request
    try {
        console.debug('[HTTP] -->', request.method, request.url);
    } catch (e) {
        // ignore logging errors
    }

    let newRequest: HttpRequest<any> = request;

    // Only modify requests to our API
    if (request.url.startsWith(environment.serverURL)) {
        // Always include credentials for cookie-based auth
        newRequest = request.clone({ withCredentials: true });

        // Add CSRF token for state-changing methods
        const csrfToken = getCsrfToken();
        if (csrfToken && ["POST", "PUT", "PATCH", "DELETE"].includes(request.method)) {
            newRequest = newRequest.clone({
                headers: newRequest.headers.set("X-CSRFToken", csrfToken),
            });
        }
    }

    return next(newRequest).pipe(
        catchError((error: HttpErrorResponse) => {
            // Handle 401 Unauthorized - try to refresh the token
            if (error.status === 401) {
                // If the app is still initializing (APP_INITIALIZER), do not attempt
                // a refresh or redirect — let the initializer handle auth state.
                if ((authService as any).initializing) {
                    console.debug('[HTTP] 401 during app init, skipping refresh/redirect for', request.url);
                    return throwError(() => error);
                }
                // If the failed request was the refresh call itself, do not attempt
                // to refresh again to avoid an infinite loop. Clear user and
                // redirect to login immediately.
                if (request.url.endsWith('/auth/refresh')) {
                    authService.user.set(null);
                    try {
                        router.navigate(["/auth/login"]);
                    } catch (e) {
                        // ignore navigation errors
                    }
                    return throwError(() => error);
                }

                // Otherwise attempt to refresh the token once, then retry original
                return authService.refreshToken().pipe(
                    switchMap(() => {
                        // Retry the original request with the new token
                        return next(newRequest);
                    }),
                    catchError((refreshError) => {
                        // Refresh failed, clear user state and redirect to login
                        authService.user.set(null);
                        try {
                            router.navigate(["/auth/login"]);
                        } catch (e) {
                            // ignore navigation errors
                        }
                        return throwError(() => refreshError);
                    }),
                );
            }

            // For other errors, just pass them through
            return throwError(() => error);
        }),
    );
};
