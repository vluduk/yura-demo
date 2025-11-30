import { ApplicationConfig, provideBrowserGlobalErrorListeners, provideZonelessChangeDetection, APP_INITIALIZER } from "@angular/core";
import { provideRouter } from "@angular/router";

import { routes } from "./app.routes";
import { provideHttpClient, withInterceptors } from "@angular/common/http";
import { Interceptor } from "@core/interceptor";
import { AuthService } from "@shared/services/auth.service";

export const appConfig: ApplicationConfig = {
    providers: [
        provideBrowserGlobalErrorListeners(),
        provideZonelessChangeDetection(),
        provideRouter(routes),
        provideHttpClient(withInterceptors([Interceptor])),
        {
            provide: APP_INITIALIZER,
            useFactory: (authService: AuthService) => () => authService.init(),
            deps: [AuthService],
            multi: true,
        },
    ],
};
