import { HttpClient } from "@angular/common/http";
import { inject, Injectable, signal, WritableSignal, Type } from "@angular/core";
import { ResumeDataType } from "@shared/types/ResumeDataType";
import { IResumeTemplate } from "@shared/types/ResumeModel";
import { ResumeTemplateType, TEMPLATES } from "@shared/types/ResumeTemplateType";
import { firstValueFrom } from "rxjs";
import { environment } from "@shared/environments/environment";

@Injectable({
    providedIn: "root",
})
export class ResumeTemplateService {
    private readonly httpClient: HttpClient = inject(HttpClient);

    public readonly isLoading: WritableSignal<boolean> = signal<boolean>(false);
    private readonly MOCK_TEMPLATES: ResumeTemplateType[] = [
        TEMPLATES["min-left-v1"],
        TEMPLATES["min-top-v1"],
        TEMPLATES["min-left-v1"],
        TEMPLATES["min-top-v1"],
    ];

    public async getTemplates(): Promise<ResumeTemplateType[]> {
        this.isLoading.set(true);
        await new Promise((resolve) => setTimeout(resolve, 300));
        this.isLoading.set(false);
        return this.MOCK_TEMPLATES;
    }

    public async getTemplateById(id: string): Promise<ResumeTemplateType | null> {
        console.log(this.MOCK_TEMPLATES.find((t) => t.id === id))
        return this.MOCK_TEMPLATES.find((t) => t.id === id) || null;
    }

    public async createResume(templateId: string): Promise<ResumeDataType> {
        // Create with mock data
        this.isLoading.set(true);
        try {
            // Simulate API delay
            await new Promise((resolve) => setTimeout(resolve, 500));

            // Mock response data
            const mockResume: ResumeDataType = {
                id: crypto.randomUUID(),
                template_id: templateId,
                title: "Нове резюме",
                is_primary: false,
                created_at: new Date(),
                updated_at: new Date(),
                personal_info: {
                    first_name: "",
                    last_name: "",
                    profession: "",
                    email: "",
                    phone: "",
                    city: "",
                    country: "",
                    address: "",
                    summary: "",
                },
                experience: [],
                education: [],
                skills: [],
                languages: [],
                extra_activities: [],
            };

            return mockResume;
        } finally {
            this.isLoading.set(false);
        }
    }
}
