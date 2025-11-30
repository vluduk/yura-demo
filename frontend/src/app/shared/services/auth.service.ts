import { HttpClient } from "@angular/common/http";
import { inject, Injectable, signal, WritableSignal } from "@angular/core";
import { environment } from "@shared/environments/environment";
import { UserType } from "@shared/types/UserType";
import { firstValueFrom, Observable, BehaviorSubject } from "rxjs";
import { UserService } from "./user.service";
import { UserSignUpRequestType } from "@shared/types/UserSignUpRequestType";
import { UserLoginRequestType } from "@shared/types/UserLoginRequestType";

interface AuthResponse {
    message: string;
    user?: {
        id: string;
        email: string;
        first_name: string;
        last_name: string;
        role: string;
    };
}

@Injectable({
    providedIn: "root",
})
export class AuthService {
    public readonly user: WritableSignal<UserType | null> = signal<UserType | null>(null);
    private readonly _initialized = new BehaviorSubject<boolean>(false);
    public readonly initialized$ = this._initialized.asObservable();

    private readonly httpClient: HttpClient = inject(HttpClient);
    private readonly userService: UserService = inject(UserService);

    /**
     * Get CSRF token from cookies
     */
    public getCsrfToken(): string | null {
        const name = "csrftoken";
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) {
            return parts.pop()?.split(";").shift() || null;
        }
        return null;
    }

    public async signUp(signUpData: UserSignUpRequestType): Promise<{ message: string }> {
        return await firstValueFrom<AuthResponse>(
            this.httpClient.post<AuthResponse>(environment.serverURL + "/auth/sign-up", signUpData),
        ).then((response: AuthResponse) => {
            // If user data is returned, update the user signal
            if (response.user) {
                this.user.set(response.user as unknown as UserType);
            } else {
                // Otherwise fetch the full user profile
                this.getAuthorizedUser();
            }

            return { message: response.message };
        });
    }

    public async login(credentials: UserLoginRequestType): Promise<{ message: string }> {
        return await firstValueFrom<AuthResponse>(
            this.httpClient.post<AuthResponse>(environment.serverURL + "/auth/login", credentials),
        ).then((response: AuthResponse) => {
            // If user data is returned, update the user signal
            if (response.user) {
                this.user.set(response.user as unknown as UserType);
            } else {
                // Otherwise fetch the full user profile
                this.getAuthorizedUser();
            }

            return { message: response.message };
        });
    }

    public async getAuthorizedUser(): Promise<UserType> {
        return await this.userService.getPersonalData().then((response: UserType) => {
            this.user.set(response);
            return response;
        });
    }

    public async logout(): Promise<{ message: string }> {
        return await firstValueFrom<{ message: string }>(
            this.httpClient.post<{ message: string }>(environment.serverURL + "/auth/logout", {}),
        ).then((response) => {
            this.user.set(null);

            return response;
        });
    }

    public refreshToken(): Observable<{ message: string }> {
        return this.httpClient.post<{ message: string }>(environment.serverURL + "/auth/refresh", {});
    }

    public async init(): Promise<void> {
        // Ensure CSRF cookie is present for subsequent state-changing requests
        await firstValueFrom(this.httpClient.get<{ message: string }>(environment.serverURL + "/auth/csrf")).catch(() => {
            // ignore errors - fallback to attempting to get authorized user
        });

        await this.getAuthorizedUser().catch(() => {
            this.user.set(null);
        });

        // Mark initialization complete so guards can proceed
        this._initialized.next(true);
    }
}
