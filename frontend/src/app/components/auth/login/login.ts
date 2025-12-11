import { Component, inject, signal, WritableSignal } from "@angular/core";
import { AuthService } from "@shared/services/auth.service";
import { Logo } from "@shared/components/logo/logo";
import { Input } from "@shared/components/input/input";
import { Button } from "@shared/components/button/button";
import { Link } from "@shared/components/link/link";
import { Router } from "@angular/router";

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

    private readonly router: Router = inject(Router);

    protected isFieldValid(field: string): boolean {
        if (!this.hasSubmitted) {
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

    private authService = inject(AuthService);

    protected async onSubmit(): Promise<void> {
        this.hasSubmitted.set(true);

        if (!this.isFieldValid("email")) {
            this.errorMessage.set("Будь ласка, введіть дійсну електронну адресу.");
            return;
        }

        if (!this.isFieldValid("password")) {
            this.errorMessage.set("Пароль повинен містити мінімум 6 символів.");
            return;
        }

        this.isLoading.set(true);

        try {
            await this.authService.login({
                email: this.email(),
                password: this.password(),
            });
            await this.router.navigate(["/"]);
        } catch (error) {
            console.error("Login failed", error);
            
            const msg: string = (error as any)?.error?.message || (error as any)?.message || 'Signup failed';
            this.errorMessage.set(msg);
        } finally {
            this.isLoading.set(false);
        }
    }
}
