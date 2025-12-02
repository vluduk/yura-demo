import {
    AfterViewInit,
    Component,
    computed,
    ElementRef,
    inject,
    Input,
    OnDestroy,
    OnInit,
    Signal,
    signal,
    Type,
    viewChild,
    WritableSignal,
} from "@angular/core";
import { HttpClient } from "@angular/common/http";
import {
    ResumeDataType,
    PersonalInfoType,
    ExperienceType,
    EducationType,
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
import { IResumeTemplate } from "@shared/types/ResumeModel";
import { NgComponentOutlet } from "@angular/common";
import html2canvas from "html2canvas";
import jsPDF from "jspdf";

type TabType = {
    id: "personal" | "experience" | "education" | "skills" | "languages";
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
        NgComponentOutlet,
    ],
    templateUrl: "./resume-builder.html",
    styleUrl: "./resume-builder.css",
})
export class ResumeBuilder implements OnInit, AfterViewInit, OnDestroy {
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

    protected readonly tabs: TabType[] = [
        { id: "personal", label: "Основне", icon: "fa-solid fa-user" },
        { id: "experience", label: "Досвід", icon: "fa-solid fa-briefcase" },
        { id: "education", label: "Освіта", icon: "fa-solid fa-graduation-cap" },
        { id: "skills", label: "Навички", icon: "fa-solid fa-tools" },
        { id: "languages", label: "Мови", icon: "fa-solid fa-language" },
    ];

    protected readonly progressWidth: Signal<number> = computed(() => {
        const tabIndex = this.tabs.findIndex((tab: TabType) => tab.id === this.activeTab());

        const progress = (tabIndex / (this.tabs.length - 1)) * 100;

        return progress;
    });

    protected readonly resumeContainer: Signal<ElementRef> = viewChild.required<ElementRef>("resumeContainer");

    private readonly httpClient: HttpClient = inject(HttpClient);
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

    ngOnInit(): void {
        // If we have a resumeId, loadResume is called by the setter.
        // If not, we might need to create one or wait.
        if (!this.currentTemplateId()) {
            this.loadTemplate("1");
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
        const template = await this.templateService.getTemplateById(id);
        console.log("Loaded template:", template);
        if (template) {
            this.template.set(template);
        }
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
            const resume = await this.resumeService.getResumeById(id);
            this.resume.set(resume);
        } catch (e) {
            console.error("Failed to load resume", e);
        } finally {
            this.isLoading.set(false);
        }
    }

    // Personal info
    public updatePersonalInfo(field: keyof PersonalInfoType, value: string): void {
        this.resumeService.updatePersonalInfo({ [field]: value });
        this.resume.set(this.resumeService.currentResume());
    }

    // Experience
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
        this.resumeService.updateExperience(id, { [field]: value });
        this.resume.set(this.resumeService.currentResume());
    }

    public removeExperience(id: string): void {
        this.resumeService.removeExperience(id);
        this.resume.set(this.resumeService.currentResume());
    }

    // Education
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
        this.resumeService.updateEducation(id, { [field]: value });
        this.resume.set(this.resumeService.currentResume());
    }

    public removeEducation(id: string): void {
        this.resumeService.removeEducation(id);
        this.resume.set(this.resumeService.currentResume());
    }

    // Skills
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

    // Languages
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
