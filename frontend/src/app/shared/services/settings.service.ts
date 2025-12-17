import { HttpClient } from "@angular/common/http";
import { inject, Injectable } from "@angular/core";
import { environment } from "@shared/environments/environment";
import { SettingsType } from "@shared/types/SettingsType";
import { firstValueFrom } from "rxjs";

@Injectable({
    providedIn: "root",
})
export class SettingsService {
    private httpClient: HttpClient = inject(HttpClient);

    public async getSettings(): Promise<SettingsType> {
        return await firstValueFrom<SettingsType>(
            this.httpClient.get<SettingsType>(`${environment.serverURL}/settings/`, { withCredentials: true })
        );
    }

    public async updateSettings(settings: Partial<SettingsType>): Promise<SettingsType> {
        return await firstValueFrom<SettingsType>(
            this.httpClient.patch<SettingsType>(`${environment.serverURL}/settings/`, settings, { withCredentials: true })
        );
    }
}
