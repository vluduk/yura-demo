import { HttpClient } from "@angular/common/http";
import { inject, Injectable } from "@angular/core";
import { environment } from "@shared/environments/environment";
import { UserRoleEnum } from "@shared/types/UserRoleEnum";
import { UserType } from "@shared/types/UserType";
import { firstValueFrom } from "rxjs";

@Injectable({
    providedIn: "root",
})
export class UserService {
    private httpClient: HttpClient = inject(HttpClient);

    public async getPersonalData(): Promise<UserType> {
        return await firstValueFrom<UserType>(this.httpClient.get<UserType>(environment.serverURL + "/auth/me"));
    }

    public async updatePersonalData(
        first_name?: string,
        last_name?: string,
        email?: string,
        phone?: string,
        avatar_url?: string,
        career_selected?: boolean,
    ): Promise<null> {
        const body: Partial<UserType> = {};

        if (first_name) {
            body.first_name = first_name;
        }
        if (last_name) {
            body.last_name = last_name;
        }
        if (email) {
            body.email = email;
        }
        if (phone) {
            body.phone = phone;
        }
        if (avatar_url) {
            body.avatar_url = avatar_url;
        }
        if (career_selected) {
            body.career_selected = career_selected;
        }

        console.log(body)

        return await firstValueFrom<null>(this.httpClient.patch<null>(environment.serverURL + "/auth/me", body));
    }

    public async deleteUser(): Promise<null> {
        return await firstValueFrom<null>(this.httpClient.delete<null>(environment.serverURL + "/auth/me"));
    }
}
