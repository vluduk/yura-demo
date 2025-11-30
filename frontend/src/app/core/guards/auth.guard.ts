import { inject } from "@angular/core";
import { CanActivateFn, Router } from "@angular/router";
import { AuthService } from "@shared/services/auth.service";
import { map, switchMap, filter, take } from "rxjs/operators";
import { Observable } from "rxjs";

export const AuthGuard: CanActivateFn = (route, state) => {
    const authService = inject(AuthService);
    const router = inject(Router);

    // Wait for AuthService initialization before checking user state
    return authService.initialized$.pipe(
        filter(initialized => initialized), // Only proceed when initialized is true
        take(1),
        map(() => {
            if (authService.user()) {
                return true;
            }
            // If not logged in, redirect to login page
            // Pass the return URL so we can redirect back after login (optional enhancement)
            return router.createUrlTree(["/auth/login"]);
        })
    );
};
