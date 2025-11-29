import { HttpClient } from "@angular/common/http";
import { inject, Injectable, signal, WritableSignal } from "@angular/core";
import { environment } from "@shared/environments/environment";
import { UserType } from "@shared/types/UserType";
import { firstValueFrom, Observable } from "rxjs";
import { UserService } from "./user.service";
import { UserSignUpRequestType } from "@shared/types/UserSignUpRequestType";
import { UserLoginRequestType } from "@shared/types/UserLoginRequestType";

@Injectable({
    providedIn: "root",
})
export class AuthService {
    public readonly user: WritableSignal<UserType | null> = signal<UserType | null>(null);

    private readonly httpClient: HttpClient = inject(HttpClient);
    private readonly userService: UserService = inject(UserService);

    public async signUp(signUpData: UserSignUpRequestType): Promise<{ message: string }> {
        return await firstValueFrom<{ message: string }>(
            this.httpClient.post<{ message: string }>(environment.serverURL + "/auth/sign-up", signUpData),
        ).then((response: { message: string }) => {
            this.getAuthorizedUser();

            return response;
        });
    }

    public async login(credentials: UserLoginRequestType): Promise<{ message: string }> {
        return await firstValueFrom<{ message: string }>(
            this.httpClient.post<{ message: string }>(environment.serverURL + "/auth/login", credentials),
        ).then((response: { message: string }) => {
            this.getAuthorizedUser();

            return response;
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
        await this.getAuthorizedUser().catch(() => {
            this.user.set(null);
        });
    }
}
