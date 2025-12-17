import { Component, inject, OnInit, signal, WritableSignal } from "@angular/core";
import { CommonModule } from "@angular/common";
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from "@angular/forms";
import { UserService } from "@shared/services/user.service";
import { SettingsService, UserSettings } from "@shared/services/settings.service";
import { Button } from "@shared/components/button/button";
import { UserType } from "@shared/types/UserType";

@Component({
    selector: "app-settings",
    standalone: true,
    imports: [CommonModule, ReactiveFormsModule, Button],
    templateUrl: "./settings.html",
    styleUrl: "./settings.css",
})
export class SettingsComponent implements OnInit {
    private userService = inject(UserService);
    private settingsService = inject(SettingsService);
    private fb = inject(FormBuilder);

    protected settingsForm: FormGroup;
    protected isLoading = signal<boolean>(false);
    protected currentUser = signal<UserType | null>(null);
    protected successMessage = signal<string | null>(null);
    protected preferredLanguage = signal<string>('uk');

    protected languageOptions = [
        { value: 'uk', label: 'Українська' },
        { value: 'en', label: 'English' },
        { value: 'ru', label: 'Русский' },
    ];

    constructor() {
        this.settingsForm = this.fb.group({
            first_name: ["", [Validators.required]],
            last_name: ["", [Validators.required]],
            email: [{ value: "", disabled: true }], // Email usually not editable directly
            phone: [""],
            preferred_language: ["uk"],
        });
    }

    ngOnInit(): void {
        this.loadUserData();
        this.loadSettings();
    }

    private async loadSettings(): Promise<void> {
        try {
            const settings = await this.settingsService.getSettings();
            this.preferredLanguage.set(settings.preferred_language || 'uk');
            this.settingsForm.patchValue({
                preferred_language: settings.preferred_language || 'uk',
            });
        } catch (error) {
            console.error("Error loading settings:", error);
        }
    }

    private async loadUserData(): Promise<void> {
        this.isLoading.set(true);
        try {
            const user = await this.userService.getPersonalData();
            this.currentUser.set(user);
            this.settingsForm.patchValue({
                first_name: user.first_name,
                last_name: user.last_name,
                email: user.email,
                phone: user.phone,
            });
        } catch (error) {
            console.error("Error loading user data:", error);
        } finally {
            this.isLoading.set(false);
        }
    }

    protected async onSubmit(): Promise<void> {
        if (this.settingsForm.invalid) return;

        this.isLoading.set(true);
        this.successMessage.set(null);

        const { first_name, last_name, phone, preferred_language } = this.settingsForm.value;

        try {
            // Update user profile
            await this.userService.updatePersonalData(first_name, last_name, undefined, phone);
            
            // Update AI settings (language preference)
            await this.settingsService.updateSettings({ preferred_language });
            
            this.successMessage.set("Дані успішно оновлено");

            // Reload to ensure sync
            await this.loadUserData();
            await this.loadSettings();
        } catch (error) {
            console.error("Error updating settings:", error);
        } finally {
            this.isLoading.set(false);
        }
    }
}
