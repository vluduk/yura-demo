import { inject } from "@angular/core";
import { CanActivateFn, Router } from "@angular/router";
import { AuthService } from "@shared/services/auth.service";

export const AuthGuard: CanActivateFn = (route, state) => {
    const authService = inject(AuthService);
    const router = inject(Router);

    // If user is logged in, allow access
    if (authService.user()) {
        return true;
    }

    // If not logged in, redirect to login page
    // Pass the return URL so we can redirect back after login (optional enhancement)
    return router.createUrlTree(["/auth/login"]);
};
