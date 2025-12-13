import {
    AfterViewInit,
    Component,
    computed,
    ElementRef,
    inject,
    Input,
    OnDestroy,
    Signal,
    signal,
    Type,
    viewChild,
    WritableSignal,
} from "@angular/core";
import {
    ResumeDataType,
    PersonalInfoType,
    ExperienceType,
    EducationType,
    ExtraActivityType,
    SkillType,
    LanguageType,
} from "@shared/types/ResumeDataType";
import { ResumeTemplateType } from "@shared/types/ResumeTemplateType";
import { ResumeTemplateService } from "@shared/services/resumeTemplate.service";
import { ResumeService } from "@shared/services/resume.service";
import { Button } from "@shared/components/button/button";
import { ResumeFormPersonal } from "@components/resume/resume-form-personal/resume-form-personal";
import { ResumeFormExperience } from "@components/resume/resume-form-experience/resume-form-experience";
import { ResumeFormEducation } from "@components/resume/resume-form-education/resume-form-education";
import { ResumeFormSkills } from "@components/resume/resume-form-skills/resume-form-skills";
import { ResumeFormLanguages } from "@components/resume/resume-form-languages/resume-form-languages";
import { ResumeFormExtraActivities } from "@components/resume/resume-form-extra-activities/resume-form-extra-activities";
import { IResumeTemplate } from "@shared/types/ResumeModel";
import { NgComponentOutlet } from "@angular/common";
import html2canvas from "html2canvas";
import jsPDF from "jspdf";
import { ResumeFormSummary } from "@components/resume/resume-form-summary/resume-form-summary";

type TabType = {
    id: "personal" | "experience" | "education" | "skills" | "languages" | "extra_activities" | "summary";
    label: string;
    icon: string;
};

@Component({
    selector: "app-resume-builder",
    imports: [
        Button,
        ResumeFormPersonal,
        ResumeFormExperience,
        ResumeFormEducation,
        ResumeFormSkills,
        ResumeFormLanguages,
        ResumeFormExtraActivities,
        ResumeFormSummary,
        NgComponentOutlet,
    ],
    templateUrl: "./resume-builder.html",
    styleUrl: "./resume-builder.css",
})
export class ResumeBuilder implements AfterViewInit, OnDestroy {
    protected readonly currentResumeId: WritableSignal<string> = signal<string>("");
    protected readonly currentTemplateId: WritableSignal<string> = signal<string>("");

    protected readonly activeTab: WritableSignal<TabType["id"]> = signal<TabType["id"]>("personal");
    protected readonly isLoading: WritableSignal<boolean> = signal<boolean>(false);

    protected readonly template: WritableSignal<ResumeTemplateType | null> = signal<ResumeTemplateType | null>(null);
    protected readonly resume: WritableSignal<ResumeDataType | null> = signal<ResumeDataType | null>(null);

    protected readonly templateComponent: Signal<Type<IResumeTemplate> | null> = computed(() => {
        return this.template()?.component ?? null;
    });

    private readonly resizeObserver: WritableSignal<ResizeObserver | null> = signal<ResizeObserver | null>(null);
    protected readonly scaleFactor: WritableSignal<number> = signal<number>(1);

    protected readonly personalInfo: Signal<PersonalInfoType | undefined> = computed(
        () => this.resume()?.personal_info,
    );
    protected readonly experiences: Signal<ExperienceType[]> = computed(() => this.resume()?.experience ?? []);
    protected readonly educations: Signal<EducationType[]> = computed(() => this.resume()?.education ?? []);
    protected readonly skills: Signal<SkillType[]> = computed(() => this.resume()?.skills ?? []);
    protected readonly languages: Signal<LanguageType[]> = computed(() => this.resume()?.languages ?? []);
    protected readonly extraActivities: Signal<ExtraActivityType[]> = computed(
        () => this.resume()?.extra_activities ?? [],
    );

    protected readonly tabs: TabType[] = [
        { id: "personal", label: "Основне", icon: "fa-solid fa-user" },
        { id: "experience", label: "Досвід", icon: "fa-solid fa-briefcase" },
        { id: "education", label: "Освіта", icon: "fa-solid fa-graduation-cap" },
        { id: "skills", label: "Навички", icon: "fa-solid fa-tools" },
        { id: "languages", label: "Мови", icon: "fa-solid fa-language" },
        { id: "extra_activities", label: "Активність", icon: "fa-solid fa-star" },
        { id: "summary", label: "Підсумок", icon: "fa-solid fa-file" },
    ];

    protected readonly topProgressWidth: Signal<number> = computed(() => {
        const tabIndex = this.tabs.findIndex((tab: TabType) => tab.id === this.activeTab());
        if (tabIndex > 2) {
            return 100;
        }

        const progress = (tabIndex / 2) * 100;

        return progress;
    });

    protected readonly bottomProgressWidth: Signal<number> = computed(() => {
        const tabIndex = this.tabs.findIndex((tab: TabType) => tab.id === this.activeTab());
        if (tabIndex < 3) {
            return 0;
        }

        const progress = ((tabIndex - 3) / (this.tabs.length - 4)) * 100;

        return progress;
    });

    protected readonly resumeContainer: Signal<ElementRef> = viewChild.required<ElementRef>("resumeContainer");

    private readonly templateService: ResumeTemplateService = inject(ResumeTemplateService);
    private readonly resumeService: ResumeService = inject(ResumeService);

    @Input()
    set resumeId(id: string) {
        this.currentResumeId.set(id);
        if (id) {
            this.loadResume(id);
        }
    }

    @Input()
    set templateId(id: string) {
        this.currentTemplateId.set(id);
        if (id) {
            this.loadTemplate(id);
        }
    }

    ngAfterViewInit() {
        this.resizeObserver.set(
            new ResizeObserver(() => {
                this.calculateScale();
            }),
        );

        this.resizeObserver()?.observe(this.resumeContainer()?.nativeElement);
    }

    ngOnDestroy() {
        if (this.resizeObserver()) {
            this.resizeObserver()?.disconnect();
        }
    }

    protected setActiveTab(tab: TabType): void {
        this.activeTab.set(tab.id);
    }

    private async loadTemplate(id: string): Promise<void> {
        await this.templateService.getTemplateById(id).then((template) => {
            this.template.set(template);
        });
    }

    calculateScale() {
        const containerWidth = this.resumeContainer()?.nativeElement.offsetWidth;
        const a4WidthPx = 794;

        if (containerWidth < a4WidthPx) {
            this.scaleFactor.set(containerWidth / a4WidthPx);
        } else {
            this.scaleFactor.set(1);
        }
    }

    private async loadResume(id: string): Promise<void> {
        this.isLoading.set(true);
        try {
            await this.resumeService.getResumeById(id).then((resume) => {
                this.resumeService.currentResume.set(resume);
                this.resume.set(resume);
            });
        } catch (e) {
            console.error("Failed to load resume", e);
        } finally {
            this.isLoading.set(false);
        }
    }

    public updatePersonalInfo(field: keyof PersonalInfoType, value: string): void {
        this.resumeService.updatePersonalInfo({ [field]: value });
        this.resume.set(this.resumeService.currentResume());
    }

    public updateSummary(summary: string): void {
        this.resumeService.updatePersonalInfo({ summary: summary });
        this.resume.set(this.resumeService.currentResume());
    }

    // Helper метод для конвертації Date в формат YYYY-MM
    private convertDateValue(value: any): any {
        if (value instanceof Date) {
            const year = value.getFullYear();
            const month = String(value.getMonth() + 1).padStart(2, '0');
            return `${year}-${month}`;
        }
        return value;
    }

    public addExperience(): void {
        const newExp: ExperienceType = {
            id: crypto.randomUUID(),
            job_title: "",
            employer: "",
        };
        this.resumeService.addExperience(newExp);
        this.resume.set(this.resumeService.currentResume());
    }

    public updateExperience(id: string, field: keyof ExperienceType, value: any): void {
        const convertedValue = (field === 'start_date' || field === 'end_date') ? this.convertDateValue(value) : value;
        this.resumeService.updateExperience(id, { [field]: convertedValue });
        this.resume.set(this.resumeService.currentResume());
    }

    public removeExperience(id: string): void {
        this.resumeService.removeExperience(id);
        this.resume.set(this.resumeService.currentResume());
    }

    public addEducation(): void {
        const newEdu: EducationType = {
            id: crypto.randomUUID(),
            institution: "",
            degree: "",
        };
        this.resumeService.addEducation(newEdu);
        this.resume.set(this.resumeService.currentResume());
    }

    public updateEducation(id: string, field: keyof EducationType, value: any): void {
        const convertedValue = (field === 'start_date' || field === 'end_date') ? this.convertDateValue(value) : value;
        this.resumeService.updateEducation(id, { [field]: convertedValue });
        this.resume.set(this.resumeService.currentResume());
    }

    public removeEducation(id: string): void {
        this.resumeService.removeEducation(id);
        this.resume.set(this.resumeService.currentResume());
    }

    public addSkill(name: string, level: SkillType["level"]): void {
        if (name.trim()) {
            const newSkill: SkillType = {
                id: crypto.randomUUID(),
                name: name.trim(),
                level,
            };
            this.resumeService.addSkill(newSkill);
            this.resume.set(this.resumeService.currentResume());
        }
    }

    public removeSkill(id: string): void {
        this.resumeService.removeSkill(id);
        this.resume.set(this.resumeService.currentResume());
    }

    public addLanguage(language: string, proficiency: LanguageType["proficiency"]): void {
        if (language.trim()) {
            const newLang: LanguageType = {
                id: crypto.randomUUID(),
                language: language.trim(),
                proficiency: proficiency,
            };
            this.resumeService.addLanguage(newLang);
            this.resume.set(this.resumeService.currentResume());
        }
    }

    public removeLanguage(id: string): void {
        this.resumeService.removeLanguage(id);
        this.resume.set(this.resumeService.currentResume());
    }

    public addExtraActivity(): void {
        const newActivity: ExtraActivityType = {
            id: crypto.randomUUID(),
            title: "",
            organization: "",
        };
        this.resumeService.addExtraActivity(newActivity);
        this.resume.set(this.resumeService.currentResume());
    }

    public updateExtraActivity(id: string, field: keyof ExtraActivityType, value: any): void {
        const convertedValue = (field === 'start_date' || field === 'end_date') ? this.convertDateValue(value) : value;
        this.resumeService.updateExtraActivity(id, { [field]: convertedValue });
        this.resume.set(this.resumeService.currentResume());
    }

    public removeExtraActivity(id: string): void {
        this.resumeService.removeExtraActivity(id);
        this.resume.set(this.resumeService.currentResume());
    }

    protected async saveResume(): Promise<void> {
        this.isLoading.set(true);
        await this.resumeService.saveResume();
        await this.downloadPdf();
        this.isLoading.set(false);
    }

    private async downloadPdf(): Promise<void> {
        const element = document.querySelector(".template") as HTMLElement;

        console.log(element);
        if (!element) {
            console.error("Template element not found in DOM");
            return;
        }

        const clone = element.cloneNode(true) as HTMLElement;

        clone.style.position = "fixed";
        clone.style.left = "-9999px";
        clone.style.top = "0";
        clone.style.transform = "none";
        clone.style.width = "210mm";
        clone.style.height = "297mm";
        clone.style.zIndex = "-1";

        document.body.appendChild(clone);

        try {
            const canvas = await html2canvas(clone, {
                scale: 2,
                useCORS: true,
                logging: false,
                width: 794,
                height: 1123,
            });

            const contentDataURL = canvas.toDataURL("image/png");

            const pdf = new jsPDF("p", "mm", "a4");

            const imgWidth = 210;
            const pageHeight = 297;

            const imgHeight = (canvas.height * imgWidth) / canvas.width;

            let heightLeft = imgHeight;
            let position = 0;

            pdf.addImage(contentDataURL, "PNG", 0, position, imgWidth, imgHeight);
            heightLeft -= pageHeight;

            // while (heightLeft > 0) {
            //     position = heightLeft - imgHeight;
            //     pdf.addPage();
            //     pdf.addImage(contentDataURL, "PNG", 0, position, imgWidth, imgHeight);
            //     heightLeft -= pageHeight;
            // }

            pdf.save("MyResume.pdf");
        } finally {
            document.body.removeChild(clone);
        }
    }
}
