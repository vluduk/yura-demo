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
        {
            id: "2",
            name: "Мінімалізм",
            preview_image: "res1.webp",
            component: null as any as Type<IResumeTemplate>,
        },
        {
            id: "3",
            name: "Креативний",
            preview_image: "res2.png",
            component: null as any as Type<IResumeTemplate>,
        },
    ];

    public async getTemplates(): Promise<ResumeTemplateType[]> {
        this.isLoading.set(true);
        await new Promise((resolve) => setTimeout(resolve, 300));
        this.isLoading.set(false);
        return this.MOCK_TEMPLATES;
    }

    public async getTemplateById(id: string): Promise<ResumeTemplateType | null> {
        await new Promise((resolve) => setTimeout(resolve, 200));
        return this.MOCK_TEMPLATES.find((t) => t.id === id) || null;
    }

    public async createResume(templateId: string): Promise<ResumeDataType> {
        // Create on backend
        this.isLoading.set(true);
        try {
            const response = await firstValueFrom(
                this.httpClient.post<any>(
                    `${environment.serverURL}/resumes/`,
                    { template_id: templateId },
                    { withCredentials: true },
                ),
            );

            // Map backend response to frontend ResumeDataType
            const resume: ResumeDataType = {
                id: response.id,
                template_id: response.template?.id,
                title: response.title,
                is_primary: response.is_primary,
                created_at: response.created_at,
                updated_at: response.updated_at,
            };

            return resume;
        } finally {
            this.isLoading.set(false);
        }
    }
}
