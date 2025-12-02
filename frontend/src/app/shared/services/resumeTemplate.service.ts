import { HttpClient } from "@angular/common/http";
import { inject, Injectable, signal, WritableSignal, Type } from "@angular/core";
import { ResumeDataType } from "@shared/types/ResumeDataType";
import { IResumeTemplate } from "@shared/types/ResumeModel";
import { ResumeTemplateType, TEMPLATES } from "@shared/types/ResumeTemplateType";

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
            preview_image: "https://cdn-images.zety.com/pages/minimalist_resume_template_1.jpg",
            component: null as any as Type<IResumeTemplate>,
        },
        {
            id: "3",
            name: "Креативний",
            preview_image: "https://cdn-images.zety.com/pages/creative_resume_template_2.jpg",
            component: null as any as Type<IResumeTemplate>,
        },
        {
            id: "4",
            name: "IT-спеціаліст",
            preview_image: "https://cdn-images.zety.com/pages/modern_resume_template_3.jpg",
            component: null as any as Type<IResumeTemplate>,
        },
        {
            id: "5",
            name: "Бізнес",
            preview_image: "https://cdn-images.zety.com/pages/professional_resume_template_1.jpg",
            component: null as any as Type<IResumeTemplate>,
        },
        {
            id: "6",
            name: "Студентський",
            preview_image: "https://cdn-images.zety.com/pages/clean_resume_template_2.jpg",
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
        // MOCK: simulate resume creation
        await new Promise((resolve) => setTimeout(resolve, 300));

        const mockResume: ResumeDataType = {
            id: crypto.randomUUID(),
            template_id: templateId,
            title: "Нове резюме",
            is_primary: false,
            created_at: new Date(),
            updated_at: new Date(),
        };

        return mockResume;

        // Original code (uncomment when backend is ready):
        // return await firstValueFrom<ResumeType>(
        //     this.httpClient.post<ResumeType>(environment.serverURL + "/resumes", {
        //         template_id: templateId,
        //     }),
        // );
    }
}
