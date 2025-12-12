import { Component, inject, model, ModelSignal, signal, WritableSignal } from "@angular/core";
import { CommonModule } from "@angular/common";
import { AuthService } from "@shared/services/auth.service";
import { Router } from "@angular/router";
import { Button } from "@shared/components/button/button";
import { Input } from "@shared/components/input/input";
import { Link } from "@shared/components/link/link";
import { Logo } from "@shared/components/logo/logo";

@Component({
    selector: "auth-signup",
    imports: [CommonModule, Logo, Input, Button, Link],
    templateUrl: "./signup.html",
    styleUrl: "./signup.css",
})
export class Signup {
    protected readonly name: WritableSignal<string> = signal<string>("");
    protected readonly surname: WritableSignal<string> = signal<string>("");
    protected readonly email: WritableSignal<string> = signal<string>("");
    protected readonly password: WritableSignal<string> = signal<string>("");
    protected readonly confirmPassword: WritableSignal<string> = signal<string>("");
    protected readonly isLoading: WritableSignal<boolean> = signal<boolean>(false);

    protected readonly errorMessage: WritableSignal<string> = signal<string>("");

    protected readonly hasSubmitted: WritableSignal<boolean> = signal<boolean>(false);

    private readonly router: Router = inject(Router);

    protected isFieldValid(field: string): boolean {
        if (!this.hasSubmitted()) {
            return true;
        }

        const emailRegExp: RegExp = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[A-Za-z]{2,}$/;

        switch (field) {
            case "name":
                return this.name().length >= 2;
            case "surname":
                return this.surname().length >= 2;
            case "email":
                return emailRegExp.test(this.email());
            case "password":
                return this.password().length >= 6 && this.password() === this.confirmPassword();
            case "confirmPassword":
                return this.confirmPassword().length >= 6 && this.confirmPassword() === this.password();
            default:
                return true;
        }
    }

    private authService = inject(AuthService);

    protected async onSubmit(): Promise<void> {
        console.log('Signup onSubmit called', {
            name: this.name(),
            surname: this.surname(),
            email: this.email(),
        });
        this.hasSubmitted.set(true);

        if (!this.isFieldValid("name")) {
            this.errorMessage.set("Ім'я повинно містити мінімум 2 символи.");
            return;
        }

        if (!this.isFieldValid("surname")) {
            this.errorMessage.set("Прізвище повинно містити мінімум 2 символи.");
            return;
        }

        if (!this.isFieldValid("email")) {
            this.errorMessage.set("Будь ласка, введіть дійсну електронну адресу.");
            return;
        }

        if (!this.isFieldValid("password") || !this.isFieldValid("confirmPassword")) {
            this.errorMessage.set("Пароль повинен містити мінімум 6 символів і збігатися в обох полях.");
            return;
        }
        
        this.isLoading.set(true);

        try {
            await this.authService.signUp({
                email: this.email(),
                first_name: this.name(),
                last_name: this.surname(),
                password: this.password(),
                phone: "1234567890", // TODO: Add phone field to signup form
            });
            
            this.router.navigate(["/"]);
        } catch (error) {
            console.error("Signup failed", error);

            const msg: string = (error as any)?.error?.message || (error as any)?.message || 'Signup failed';
            this.errorMessage.set(msg);

            setTimeout(() => this.errorMessage.set(""), 3000);
        } finally {
            this.isLoading.set(false);
        }
    }
}
