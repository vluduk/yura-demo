import { Component, OnInit, inject, signal, WritableSignal } from "@angular/core";
import { CommonModule } from "@angular/common";
import { Router, RouterModule } from "@angular/router";
import { ResumeService } from "@shared/services/resume.service";
import { ResumeDataType } from "@shared/types/ResumeDataType";
import { Button } from "@shared/components/button/button";
import { TEMPLATES } from "@shared/types/ResumeTemplateType";
import { Title } from "@shared/components/title/title";

@Component({
    selector: "app-resume-library",
    standalone: true,
    imports: [CommonModule, RouterModule, Button, Title],
    templateUrl: "./library.html",
    styleUrl: "./library.css",
})
export class Library implements OnInit {
    private readonly resumeService = inject(ResumeService);
    private readonly router = inject(Router);

    protected readonly resumes: WritableSignal<ResumeDataType[]> = signal<ResumeDataType[]>([]);
    protected readonly isLoading = this.resumeService.isLoading;

    ngOnInit(): void {
        this.loadResumes();
    }

    private async loadResumes(): Promise<void> {
        const list = await this.resumeService.getResumes();
        this.resumes.set(list);
    }

    protected createNew(): void {
        this.router.navigate(["/resume-templates"]);
    }

    protected viewResume(id: string): void {
        const resume = this.resumes().find(r => r.id === id);
        if (resume) {
            this.resumeService.currentResume.set(resume);
        }
        this.router.navigate(["/resume-builder", id], { queryParams: { templateId: this.getTemplateId(id) } });
    }

    protected getTemplateName(templateId: string): string {
        return TEMPLATES[templateId]?.name || "Невідомий шаблон";
    }

    protected getTemplateId(resumeId: string): string {
        const resume = this.resumes().find(r => r.id === resumeId);
        return TEMPLATES[resume!.template_id]?.id || "min-left-v1";
    }

    protected formatDate(dateStr?: string | Date): string {
        if (!dateStr) {
            return "";
        }

        return new Date(dateStr).toLocaleDateString("uk-UA", {
            day: "numeric",
            month: "short",
            year: "numeric",
        });
    }

    protected updateTitle(resumeId: string, event: Event): void {
        const newTitle = (event.target as HTMLElement).innerText;
        this.resumes.update(resumes =>
            resumes.map(r => r.id === resumeId ? { ...r, title: newTitle } : r)
        );
    }

    protected async saveResume(event: Event, resume: ResumeDataType): Promise<void> {
        event.stopPropagation(); // Prevent navigation to builder
        try {
            await this.resumeService.saveResume(resume);
            // Optional: Show success notification
        } catch (error) {
            console.error("Failed to save resume", error);
        }
    }
}
