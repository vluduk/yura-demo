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

    private createEmptyResume(id: string, templateId: string): ResumeDataType {
        return {
            id,
            template_id: templateId,
            title: "Нове резюме",
            is_primary: false,
        };
    }

    public async getResumeById(id: string): Promise<ResumeDataType> {
        this.isLoading.set(true);
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
        } finally {
            this.isLoading.set(false);
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

        this.isLoading.set(true);
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
        } finally {
            this.isLoading.set(false);
        }
    }
    
    public async createResume(templateId: string): Promise<ResumeDataType> {
        this.isLoading.set(true);
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
        } finally {
            this.isLoading.set(false);
        }
    }

    public async generateAIContent(resumeId: string, field: string, context?: any): Promise<string> {
        this.isLoading.set(true);
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
        } finally {
            this.isLoading.set(false);
        }
    }
}
