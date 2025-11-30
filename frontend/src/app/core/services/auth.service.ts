import { Injectable, signal, WritableSignal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap } from 'rxjs';
import { Router } from '@angular/router';

export interface SignupRequest {
    email: string;
    name: string;
    surname: string;
    role: string;
    password: string;
}

export interface LoginRequest {
    email: string;
    password: string;
}

export interface AuthResponse {
    message: string;
}

@Injectable({
    providedIn: 'root'
})
export class AuthService {
    private readonly apiUrl = 'http://localhost:8000/api/v1/auth';
    private readonly isAuthenticatedSignal: WritableSignal<boolean> = signal(false);

    constructor(
        private http: HttpClient,
        private router: Router
    ) { }

    get isAuthenticated(): boolean {
        return this.isAuthenticatedSignal();
    }

    signup(data: SignupRequest): Observable<AuthResponse> {
        return this.http.post<AuthResponse>(`${this.apiUrl}/sign-up`, data, { withCredentials: true })
            .pipe(
                tap(() => {
                    this.isAuthenticatedSignal.set(true);
                })
            );
    }

    login(data: LoginRequest): Observable<AuthResponse> {
        return this.http.post<AuthResponse>(`${this.apiUrl}/login`, data, { withCredentials: true })
            .pipe(
                tap(() => {
                    this.isAuthenticatedSignal.set(true);
                })
            );
    }

    logout(): Observable<AuthResponse> {
        return this.http.post<AuthResponse>(`${this.apiUrl}/logout`, {}, { withCredentials: true })
            .pipe(
                tap(() => {
                    this.isAuthenticatedSignal.set(false);
                    this.router.navigate(['/auth/login']);
                })
            );
    }

    refreshToken(): Observable<AuthResponse> {
        return this.http.post<AuthResponse>(`${this.apiUrl}/refresh`, {}, { withCredentials: true });
    }
}
