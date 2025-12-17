import { HttpClient } from "@angular/common/http";
import { inject, Injectable } from "@angular/core";
import { environment } from "@shared/environments/environment";
import { firstValueFrom } from "rxjs";

export interface UserSettings {
    preferred_language: string;
}

@Injectable({
    providedIn: "root",
})
export class SettingsService {
    private httpClient: HttpClient = inject(HttpClient);

    public async getSettings(): Promise<UserSettings> {
        return await firstValueFrom<UserSettings>(
            this.httpClient.get<UserSettings>(`${environment.serverURL}/settings/`, { withCredentials: true })
        );
    }

    public async updateSettings(settings: Partial<UserSettings>): Promise<UserSettings> {
        return await firstValueFrom<UserSettings>(
            this.httpClient.patch<UserSettings>(`${environment.serverURL}/settings/`, settings, { withCredentials: true })
        );
    }
}
