import { Component, inject, signal, WritableSignal } from "@angular/core";
import { Router } from "@angular/router";
import { Button } from "@shared/components/button/button";
import { Input } from "@shared/components/input/input";
import { Link } from "@shared/components/link/link";
import { Logo } from "@shared/components/logo/logo";

@Component({
    selector: "auth-signup",
    imports: [Logo, Input, Button, Link],
    templateUrl: "./signup.html",
    styleUrl: "./signup.css",
})
export class Signup {
    protected name: WritableSignal<string> = signal<string>("");
    protected surname: WritableSignal<string> = signal<string>("");
    protected email: WritableSignal<string> = signal<string>("");
    protected password: WritableSignal<string> = signal<string>("");
    protected confirmPassword: WritableSignal<string> = signal<string>("");

    protected isLoading: WritableSignal<boolean> = signal<boolean>(false);

    private hasSubmitted: boolean = false;

    private router: Router = inject(Router);

    protected isFieldValid(field: string): boolean {
        if (!this.hasSubmitted) {
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

    protected async onSubmit(): Promise<void> {
        this.hasSubmitted = true;

        if (
            !this.email() ||
            !this.name() ||
            !this.surname() ||
            !this.password() ||
            !this.confirmPassword() ||
            this.password() !== this.confirmPassword()
        ) {
            return;
        }

        this.isLoading.set(true);

        console.log("Submitting signup form with:", {
            name: this.name(),
            surname: this.surname(),
            email: this.email(),
            password: this.password(),
        });
    }
}
