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
    styleUrls: ["./signup.css"],
})
export class Signup {
    protected name: ModelSignal<string> = model<string>("");
    protected surname: ModelSignal<string> = model<string>("");
    protected email: ModelSignal<string> = model<string>("");
    protected password: ModelSignal<string> = model<string>("");
    protected confirmPassword: ModelSignal<string> = model<string>("");

    protected isLoading: WritableSignal<boolean> = signal<boolean>(false);
    protected errorMessage: WritableSignal<string | null> = signal<string | null>(null);

    protected hasSubmitted: WritableSignal<boolean> = signal<boolean>(false);

    private router: Router = inject(Router);

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

        if (
            !this.isFieldValid("email") ||
            !this.isFieldValid("name") ||
            !this.isFieldValid("surname") ||
            !this.isFieldValid("password") ||
            !this.isFieldValid("confirmPassword")
        ) {
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
            await this.router.navigate(["/conversation"]);
        } catch (error) {
            console.error("Signup failed", error);
            const msg = (error as any)?.error?.message || (error as any)?.message || 'Signup failed';
            this.errorMessage.set(String(msg));
        } finally {
            this.isLoading.set(false);
        }
    }
}
