import { Component, inject, OnInit, signal, WritableSignal } from "@angular/core";
import { Button } from "@shared/components/button/button";
import { SettingsService } from "@shared/services/settings.service";
import { Select } from "@shared/components/select/select";

@Component({
    selector: "cabinet-settings",
    imports: [Button, Select],
    templateUrl: "./settings.html",
    styleUrl: "./settings.css",
})
export class Settings implements OnInit {
    protected readonly preferredLanguage: WritableSignal<string> = signal<string>('uk');

    protected readonly languageOptions = [
        { value: 'uk', label: 'Українська' },
        { value: 'en', label: 'English' },
        { value: 'ru', label: 'Русский' },
    ];

    protected readonly isLoading: WritableSignal<boolean> = signal<boolean>(false);
    protected readonly errorMessage: WritableSignal<string> = signal<string>("");

    private readonly settingsService: SettingsService = inject(SettingsService);

    ngOnInit(): void {
        this.loadSettings();
    }

    private async loadSettings(): Promise<void> {
        try {
            const settings = await this.settingsService.getSettings();

            this.preferredLanguage.set(settings.preferred_language || 'uk');
        } catch (error) {
            console.error("Error loading settings:", error);
        }
    }

    protected async onSubmit(): Promise<void> {
        this.isLoading.set(true);

        try {
            await this.settingsService.updateSettings({ preferred_language: this.preferredLanguage() });

            await this.loadSettings();
        } catch (error) {
            console.error("Error updating settings:", error);

            this.errorMessage.set("Сталась помилка під час збереження налаштувань.");
            setTimeout(() => this.errorMessage.set(""), 5000);
        } finally {
            this.isLoading.set(false);
        }
    }    
}
