import { inject, Injectable, signal, WritableSignal } from "@angular/core";
import { HttpClient } from "@angular/common/http";
import { environment } from "@shared/environments/environment";
import { firstValueFrom } from "rxjs";
import {
    ResumeDataType,
    PersonalInfoType,
    ExperienceType,
    EducationType,
    ExtraActivityType,
    SkillType,
    LanguageType,
} from "@shared/types/ResumeDataType";

@Injectable({
    providedIn: "root",
})
export class ResumeService {
    private httpClient = inject(HttpClient);
    public readonly currentResume: WritableSignal<ResumeDataType | null> = signal<ResumeDataType | null>(null);
    public readonly isLoading: WritableSignal<boolean> = signal<boolean>(false);

    // Mock data for resume library
    private readonly MOCK_RESUMES: ResumeDataType[] = [
        {
            id: "resume-1",
            template_id: "min-left-v1",
            title: "Frontend Developer",
            is_primary: true,
            created_at: new Date("2024-01-15"),
            updated_at: new Date("2024-12-01"),
            personal_info: {
                first_name: "Олександр",
                last_name: "Петренко",
                profession: "Frontend Developer",
                email: "o.petrenko@example.com",
                phone: "+380501234567",
                city: "Київ",
                country: "Україна",
                summary: "Досвідчений frontend розробник з 3+ роками досвіду роботи з React, Angular та Vue.js. Спеціалізуюся на створенні адаптивних та користувацьких інтерфейсів."
            },
            experience: [
                {
                    id: "exp-1",
                    job_title: "Senior Frontend Developer",
                    employer: "TechCorp Ukraine",
                    city: "Київ",
                    start_date: new Date("2022-03-01"),
                    end_date: new Date("2024-12-01"),
                    is_current: true,
                    description: "Розробка та підтримка веб-додатків з використанням Angular 15+, TypeScript та RxJS. Оптимізація продуктивності додатків та впровадження best practices."
                }
            ],
            education: [
                {
                    id: "edu-1",
                    institution: "Київський політехнічний інститут",
                    degree: "Бакалавр",
                    field_of_study: "Комп'ютерна інженерія",
                    start_date: new Date("2018-09-01"),
                    end_date: new Date("2022-06-30"),
                    is_current: false
                }
            ],
            skills: [
                { id: "skill-1", name: "Angular", level: "Expert" },
                { id: "skill-2", name: "TypeScript", level: "Advanced" },
                { id: "skill-3", name: "JavaScript", level: "Expert" },
                { id: "skill-4", name: "HTML/CSS", level: "Expert" }
            ],
            languages: [
                { id: "lang-1", language: "Українська", proficiency: "native" },
                { id: "lang-2", language: "Англійська", proficiency: "b2" },
                { id: "lang-3", language: "Польська", proficiency: "a2" }
            ],
            extra_activities: []
        },
        {
            id: "resume-2",
            template_id: "min-top-v1",
            title: "Project Manager",
            is_primary: false,
            created_at: new Date("2024-02-20"),
            updated_at: new Date("2024-11-15"),
            personal_info: {
                first_name: "Марія",
                last_name: "Коваленко",
                profession: "IT Project Manager",
                email: "m.kovalenko@example.com",
                phone: "+380677654321",
                city: "Львів",
                country: "Україна",
                summary: "Досвідчений проектний менеджер з 5+ роками роботи в IT сфері. Експертиза в Agile/Scrum методологіях та управлінні командами до 15 осіб."
            },
            experience: [
                {
                    id: "exp-2",
                    job_title: "Senior Project Manager",
                    employer: "SoftServe",
                    city: "Львів",
                    start_date: new Date("2021-01-15"),
                    end_date: new Date("2024-11-15"),
                    is_current: true,
                    description: "Управління проектами розробки мобільних та веб додатків. Координація роботи розподілених команд та взаємодія з міжнародними клієнтами."
                },
                {
                    id: "exp-3",
                    job_title: "Project Manager",
                    employer: "EPAM Systems",
                    city: "Київ",
                    start_date: new Date("2019-06-01"),
                    end_date: new Date("2020-12-31"),
                    is_current: false,
                    description: "Планування та контроль виконання проектів в галузі фінтеху. Впровадження Agile практик та оптимізація процесів розробки."
                }
            ],
            education: [
                {
                    id: "edu-2",
                    institution: "Львівський національний університет",
                    degree: "Магістр",
                    field_of_study: "Менеджмент організацій",
                    start_date: new Date("2016-09-01"),
                    end_date: new Date("2018-06-30"),
                    is_current: false
                }
            ],
            skills: [
                { id: "skill-5", name: "Scrum/Agile", level: "Expert" },
                { id: "skill-6", name: "Jira", level: "Advanced" },
                { id: "skill-7", name: "Risk Management", level: "Advanced" },
                { id: "skill-8", name: "Team Leadership", level: "Expert" }
            ],
            languages: [
                { id: "lang-4", language: "Українська", proficiency: "native" },
                { id: "lang-5", language: "Англійська", proficiency: "c1" },
                { id: "lang-6", language: "Німецька", proficiency: "b1" }
            ],
            extra_activities: [
                {
                    id: "act-1",
                    title: "Ментор стартапів",
                    organization: "Львів IT Кластер",
                    start_date: new Date("2022-01-01"),
                    is_current: true,
                    description: "Консультування молодих стартапів з питань планування проектів та побудови команд."
                }
            ]
        },
        {
            id: "resume-3",
            template_id: "min-left-v1",
            title: "UX/UI Designer",
            is_primary: false,
            created_at: new Date("2024-03-10"),
            updated_at: new Date("2024-10-20"),
            personal_info: {
                first_name: "Анна",
                last_name: "Мельник",
                profession: "UX/UI Designer",
                email: "a.melnyk@example.com",
                phone: "+380631234567",
                city: "Харків",
                country: "Україна",
                summary: "Креативний UX/UI дизайнер з пристрастю до створення інтуїтивних інтерфейсів. 4+ роки досвіду в дизайні мобільних та веб додатків."
            },
            experience: [
                {
                    id: "exp-4",
                    job_title: "UX/UI Designer",
                    employer: "Design Studio Pro",
                    city: "Харків",
                    start_date: new Date("2021-08-01"),
                    end_date: new Date("2024-10-20"),
                    is_current: true,
                    description: "Дизайн користувацьких інтерфейсів для e-commerce платформ. Проведення UX досліджень та тестування юзабіліті."
                }
            ],
            education: [
                {
                    id: "edu-3",
                    institution: "Харківський національний університет",
                    degree: "Бакалавр",
                    field_of_study: "Графічний дизайн",
                    start_date: new Date("2017-09-01"),
                    end_date: new Date("2021-06-30"),
                    is_current: false
                }
            ],
            skills: [
                { id: "skill-9", name: "Figma", level: "Expert" },
                { id: "skill-10", name: "Adobe Creative Suite", level: "Advanced" },
                { id: "skill-11", name: "Prototyping", level: "Advanced" },
                { id: "skill-12", name: "User Research", level: "Intermediate" }
            ],
            languages: [
                { id: "lang-7", language: "Українська", proficiency: "native" },
                { id: "lang-8", language: "Англійська", proficiency: "b2" }
            ],
            extra_activities: []
        }
    ];

    public async getResumes(): Promise<ResumeDataType[]> {
        this.isLoading.set(true);
        try {
            // Simulate API delay
            await new Promise(resolve => setTimeout(resolve, 800));
            return [...this.MOCK_RESUMES];
        } finally {
            this.isLoading.set(false);
        }
    }

    private createEmptyResume(id: string, templateId: string): ResumeDataType {
        return {
            id,
            template_id: templateId,
            title: "Нове резюме",
            is_primary: false,
        };
    }

    public async getResumeById(id: string): Promise<ResumeDataType> {
        return this.MOCK_RESUMES.find(resume => resume.id === id) || this.createEmptyResume(id, "1");
        
        try {
            const response = await firstValueFrom(
                this.httpClient.get<any>(`${environment.serverURL}/resumes/${id}/`, {
                    withCredentials: true,
                })
            );

            // Map backend response to frontend structure
            const resume: ResumeDataType = {
                id: response.id,
                template_id: response.template?.id,
                title: response.title,
                is_primary: response.is_primary,
                created_at: response.created_at,
                updated_at: response.updated_at,
                personal_info: {
                    first_name: response.first_name,
                    last_name: response.last_name,
                    profession: response.profession,
                    summary: response.professional_summary,
                    email: response.contact_details?.email,
                    phone: response.contact_details?.phone,
                    address: response.contact_details?.address,
                    city: response.contact_details?.city,
                    country: response.contact_details?.country,
                },
                experience: response.experience_entries,
                education: response.education_entries,
                extra_activities: response.extra_activity_entries,
                skills: response.skill_entries,
                languages: response.language_entries,
            };

            this.currentResume.set(resume);
            return resume;
        } catch (error) {
            console.error("Error fetching resume:", error);
            // Fallback for new resume creation flow if ID is 'new' or similar, 
            // but usually we should handle creation separately.
            // For now, if error, return empty/mock if it matches a pattern or throw.
            // Assuming 'new' might be passed or we just want to be robust:
            const empty = this.createEmptyResume(id, "1");
            this.currentResume.set(empty);
            return empty;
        }
    }

    public updatePersonalInfo(data: Partial<PersonalInfoType>): void {
        const resume = this.currentResume();
        if (resume) {
            this.currentResume.set({
                ...resume,
                personal_info: {
                    first_name: data.first_name ?? resume.personal_info?.first_name ?? "",
                    last_name: data.last_name ?? resume.personal_info?.last_name ?? "",
                    profession: data.profession ?? resume.personal_info?.profession ?? "",
                    email: data.email ?? resume.personal_info?.email ?? "",
                    phone: data.phone ?? resume.personal_info?.phone ?? "",
                    address: data.address ?? resume.personal_info?.address ?? "",
                    city: data.city ?? resume.personal_info?.city ?? "",
                    country: data.country ?? resume.personal_info?.country ?? "",
                    summary: data.summary ?? resume.personal_info?.summary ?? "",
                },
            });
        }
    }

    public addExperience(experience: ExperienceType): void {
        const resume = this.currentResume();
        if (resume) {
            this.currentResume.set({
                ...resume,
                experience: [...(resume.experience ?? []), experience],
            });
        }
    }

    public updateExperience(id: string, data: Partial<ExperienceType>): void {
        const resume = this.currentResume();
        if (resume) {
            this.currentResume.set({
                ...resume,
                experience: (resume.experience ?? []).map((exp) => (exp.id === id ? { ...exp, ...data } : exp)),
            });
        }
    }

    public removeExperience(id: string): void {
        const resume = this.currentResume();
        if (resume) {
            this.currentResume.set({
                ...resume,
                experience: (resume.experience ?? []).filter((exp) => exp.id !== id),
            });
        }
    }

    public addEducation(education: EducationType): void {
        const resume = this.currentResume();
        if (resume) {
            this.currentResume.set({
                ...resume,
                education: [...(resume.education ?? []), education],
            });
        }
    }

    public updateEducation(id: string, data: Partial<EducationType>): void {
        const resume = this.currentResume();
        if (resume) {
            this.currentResume.set({
                ...resume,
                education: (resume.education ?? []).map((edu) => (edu.id === id ? { ...edu, ...data } : edu)),
            });
        }
    }

    public removeEducation(id: string): void {
        const resume = this.currentResume();
        if (resume) {
            this.currentResume.set({
                ...resume,
                education: (resume.education ?? []).filter((edu) => edu.id !== id),
            });
        }
    }

    public addSkill(skill: SkillType): void {
        const resume = this.currentResume();
        if (resume) {
            this.currentResume.set({
                ...resume,
                skills: [...(resume.skills ?? []), skill],
            });
        }
    }

    public removeSkill(id: string): void {
        const resume = this.currentResume();
        if (resume) {
            this.currentResume.set({
                ...resume,
                skills: (resume.skills ?? []).filter((skill) => skill.id !== id),
            });
        }
    }

    public addLanguage(language: LanguageType): void {
        const resume = this.currentResume();
        if (resume) {
            this.currentResume.set({
                ...resume,
                languages: [...(resume.languages ?? []), language],
            });
        }
    }

    public removeLanguage(id: string): void {
        const resume = this.currentResume();
        if (resume) {
            this.currentResume.set({
                ...resume,
                languages: (resume.languages ?? []).filter((lang) => lang.id !== id),
            });
        }
    }

    public addExtraActivity(activity: ExtraActivityType): void {
        const resume = this.currentResume();
        if (resume) {
            this.currentResume.set({
                ...resume,
                extra_activities: [...(resume.extra_activities ?? []), activity],
            });
        }
    }

    public updateExtraActivity(id: string, data: Partial<ExtraActivityType>): void {
        const resume = this.currentResume();
        if (resume) {
            this.currentResume.set({
                ...resume,
                extra_activities: (resume.extra_activities ?? []).map((act) => (act.id === id ? { ...act, ...data } : act)),
            });
        }
    }

    public removeExtraActivity(id: string): void {
        const resume = this.currentResume();
        if (resume) {
            this.currentResume.set({
                ...resume,
                extra_activities: (resume.extra_activities ?? []).filter((act) => act.id !== id),
            });
        }
    }

    public async saveResume(): Promise<void> {
        const resume = this.currentResume();
        if (!resume) return;

        try {
            // If it's a new resume (no ID or temp ID), we might need POST, but here we assume ID exists or we use PUT/PATCH
            // If ID is UUID, it's likely existing.
            // For simplicity, we'll try PUT to update.
            // If the ID is not valid on server, this will fail.
            // Ideally, we should have createResume() method.
            
            await firstValueFrom(
                this.httpClient.put(`${environment.serverURL}/resumes/${resume.id}/`, resume, {
                    withCredentials: true,
                })
            );
            console.log("Resume saved successfully");
        } catch (error) {
            console.error("Error saving resume:", error);
            // If resume doesn't exist on server (client generated id), create it via POST
            // Detect HTTP 404 from Angular HttpErrorResponse
            const status = (error as any)?.status;
            if (status === 404) {
                try {
                    const created = await firstValueFrom(
                        this.httpClient.post<any>(`${environment.serverURL}/resumes/`, resume, { withCredentials: true })
                    );
                    // Map response to local structure and set currentResume
                    const mapped: ResumeDataType = {
                        id: created.id,
                        template_id: created.template?.id,
                        title: created.title,
                        personal_info: {
                            first_name: created.first_name,
                            last_name: created.last_name,
                            profession: created.profession,
                            summary: created.professional_summary,
                            email: created.contact_details?.email,
                            phone: created.contact_details?.phone,
                            address: created.contact_details?.address,
                            city: created.contact_details?.city,
                            country: created.contact_details?.country,
                        },
                        experience: created.experience_entries,
                        education: created.education_entries,
                        extra_activities: created.extra_activity_entries,
                        skills: created.skill_entries,
                        languages: created.language_entries,
                        is_primary: created.is_primary,
                        created_at: created.created_at,
                        updated_at: created.updated_at,
                    };
                    this.currentResume.set(mapped);
                    console.log("Resume created on server and saved locally");
                } catch (createErr) {
                    console.error("Failed to create resume after 404:", createErr);
                }
            }
        }
    }
    
    public async createResume(templateId: string): Promise<ResumeDataType> {
        try {
            const newResume = await firstValueFrom(
                this.httpClient.post<ResumeDataType>(`${environment.serverURL}/resumes/`, {
                    template_id: templateId,
                    title: "Нове резюме"
                }, {
                    withCredentials: true,
                })
            );
            this.currentResume.set(newResume);
            return newResume;
        } catch (error) {
            console.error("Error creating resume:", error);
            throw error;
        }
    }

    public async generateAIContent(resumeId: string, field: string, context?: any): Promise<string> {
        try {
            const response = await firstValueFrom(
                this.httpClient.post<{ content: string }>(
                    `${environment.serverURL}/resumes/${resumeId}/ai-suggest/`,
                    { field, context },
                    { withCredentials: true }
                )
            );
            return response.content;
        } catch (error) {
            console.error("Error generating AI content:", error);
            return "";
        }
    }
}
