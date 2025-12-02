import { Injectable, signal, WritableSignal } from "@angular/core";
import {
    ResumeDataType,
    PersonalInfoType,
    ExperienceType,
    EducationType,
    SkillType,
    LanguageType,
} from "@shared/types/ResumeDataType";

@Injectable({
    providedIn: "root",
})
export class ResumeService {
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
        await new Promise((resolve) => setTimeout(resolve, 300));

        // MOCK: return empty resume or existing one
        const resume = this.currentResume() || this.createEmptyResume(id, "1");
        this.currentResume.set(resume);
        this.isLoading.set(false);
        return resume;
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

    public async saveResume(): Promise<void> {
        this.isLoading.set(true);
        await new Promise((resolve) => setTimeout(resolve, 500));
        console.log("Resume saved:", this.currentResume());
        this.isLoading.set(false);
    }
}
