import { Component, inject, signal, WritableSignal } from "@angular/core";
import { Logo } from "@shared/components/logo/logo";
import { Input } from "@shared/components/input/input";
import { Button } from "@shared/components/button/button";
import { Link } from "@shared/components/link/link";
import { Router } from "@angular/router";
import { AuthService } from "@core/services/auth.service";

@Component({
    selector: "auth-login",
    imports: [Logo, Input, Button, Link],
    templateUrl: "./login.html",
    styleUrl: "./login.css",
})
export class Login {
    protected readonly email: WritableSignal<string> = signal<string>("");
    protected readonly password: WritableSignal<string> = signal<string>("");

    protected readonly isLoading: WritableSignal<boolean> = signal<boolean>(false);
    protected readonly errorMessage: WritableSignal<string> = signal<string>("");

    private readonly hasSubmitted: WritableSignal<boolean> = signal<boolean>(false);

    private router: Router = inject(Router);
    private authService: AuthService = inject(AuthService);

    protected isFieldValid(field: string): boolean {
        if (!this.hasSubmitted()) {
            return true;
        }

        const emailRegExp: RegExp = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[A-Za-z]{2,}$/;

        switch (field) {
            case "email":
                return emailRegExp.test(this.email());
            case "password":
                return this.password().length >= 6;
            default:
                return true;
        }
    }

    protected async onSubmit(): Promise<void> {
        this.hasSubmitted.set(true);
        this.errorMessage.set("");

        if (!this.email() || !this.password()) {
            return;
        }

        this.isLoading.set(true);

        this.authService.login({
            email: this.email(),
            password: this.password()
        }).subscribe({
            next: () => {
                this.router.navigate(['/']);
            },
            error: (error) => {
                this.errorMessage.set(error.error?.message || 'Login failed');
                this.isLoading.set(false);
            },
            complete: () => {
                this.isLoading.set(false);
            }
        });
    }
}
