import { Component, effect, inject, signal, WritableSignal } from "@angular/core";
import { Button } from "@shared/components/button/button";
import { CabinetPopupService } from "@shared/services/cabinetPopup.service";
import { UserService } from "@shared/services/user.service";
import { UserType } from "@shared/types/UserType";
import { Input } from "@shared/components/input/input";

@Component({
    selector: "cabinet-account",
    imports: [Button, Input],
    templateUrl: "./account.html",
    styleUrl: "./account.css",
})
export class Account {
    protected readonly currentUser: WritableSignal<UserType | null> = signal<UserType | null>(null);

    protected readonly userFirstName: WritableSignal<string> = signal<string>("");
    protected readonly userLastName: WritableSignal<string> = signal<string>("");
    protected readonly userPhone: WritableSignal<string> = signal<string>("");
    protected readonly userEmail: WritableSignal<string> = signal<string>("");

    protected readonly isLoading: WritableSignal<boolean> = signal<boolean>(false);
    protected readonly errorMessage: WritableSignal<string> = signal<string>("");

    private readonly userService: UserService = inject(UserService);
    private readonly cabinetPopupService: CabinetPopupService = inject(CabinetPopupService);

    constructor() {
        effect(() => {
            if (this.cabinetPopupService.isVisible()) {
                this.loadUserData();
            }
        });
    }

    ngOnInit(): void {
        this.loadUserData();
    }

    private async loadUserData(): Promise<void> {
        this.isLoading.set(true);
        try {
            const user = await this.userService.getPersonalData();

            this.currentUser.set(user);
            this.userFirstName.set(user?.first_name ?? "");
            this.userLastName.set(user?.last_name ?? "");
            this.userPhone.set(user?.phone ?? "");
            this.userEmail.set(user?.email ?? "");
        } catch (error) {
            console.error("Error loading user data:", error);
        } finally {
            this.isLoading.set(false);
        }
    }

    private isFieldValid(field: string): boolean {
        const emailRegExp: RegExp = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[A-Za-z]{2,}$/;

        switch (field) {
            case "name":
                return this.userFirstName().length >= 2;
            case "surname":
                return this.userLastName().length >= 2;
            case "email":
                return emailRegExp.test(this.userEmail());
            case "phone":
                return !this.userPhone() || this.userPhone().length === 10;
            default:
                return true;
        }
    }

    protected async onSubmit(): Promise<void> {
        if (!this.isFieldValid("name")) {
            this.errorMessage.set("Ім'я повинно містити щонайменше 2 символи.");

            setTimeout(() => this.errorMessage.set(""), 5000);
            return;
        }

        if (!this.isFieldValid("surname")) {
            this.errorMessage.set("Прізвище повинно містити щонайменше 2 символи.");

            setTimeout(() => this.errorMessage.set(""), 5000);
            return;
        }

        if (!this.isFieldValid("phone")) {
            this.errorMessage.set("Номер телефону некоректний.");

            setTimeout(() => this.errorMessage.set(""), 5000);
            return;
        }

        if (!this.isFieldValid("email")) {
            this.errorMessage.set("Електронна пошта некоректна.");

            setTimeout(() => this.errorMessage.set(""), 5000);
            return;
        }

        if (this.currentUser()?.first_name === this.userFirstName() &&
            this.currentUser()?.last_name === this.userLastName() &&
            this.currentUser()?.email === this.userEmail() &&
            this.currentUser()?.phone === this.userPhone()
        ) {
            return;
        }

        this.isLoading.set(true);

        try {
            await this.userService.updatePersonalData(
                this.currentUser()?.first_name !== this.userFirstName() ? this.userFirstName() : undefined,
                this.currentUser()?.last_name !== this.userLastName() ? this.userLastName() : undefined,
                this.currentUser()?.email !== this.userEmail() ? this.userEmail() : undefined,
                this.currentUser()?.phone !== this.userPhone() ? this.userPhone() : undefined
            );

            await this.loadUserData();
        } catch (error) {
            console.error("Error updating account:", error);
        } finally {
            this.isLoading.set(false);
        }
    }

}
