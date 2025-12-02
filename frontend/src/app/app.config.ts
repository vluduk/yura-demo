import {
    ApplicationConfig,
    provideBrowserGlobalErrorListeners,
    provideZonelessChangeDetection,
    APP_INITIALIZER,
} from "@angular/core";
import { provideRouter, withComponentInputBinding } from "@angular/router";

import { routes } from "./app.routes";
import { provideHttpClient, withInterceptors } from "@angular/common/http";
import { Interceptor } from "@core/interceptor";
import { AuthService } from "@shared/services/auth.service";
import { provideMarkdown } from "ngx-markdown";

export const appConfig: ApplicationConfig = {
    providers: [
        provideBrowserGlobalErrorListeners(),
        provideZonelessChangeDetection(),
        provideRouter(routes, withComponentInputBinding()),
        provideHttpClient(withInterceptors([Interceptor])),
        provideMarkdown(),
        {
            provide: APP_INITIALIZER,
            useFactory: (authService: AuthService) => () => authService.init(),
            deps: [AuthService],
            multi: true,
        },
    ],
};
