import { Component, inject, OnInit, signal, WritableSignal } from "@angular/core";
import { Router } from "@angular/router";
import { Title } from "@shared/components/title/title";
import { ResumeTemplateService } from "@shared/services/resumeTemplate.service";
import { ResumeTemplateType } from "@shared/types/ResumeTemplateType";
import { ResumeTemplateCard } from "@components/resume/resume-template-card/resume-template-card";

@Component({
    selector: "app-resume-template-list",
    imports: [Title, ResumeTemplateCard],
    templateUrl: "./resume-template-list.html",
    styleUrl: "./resume-template-list.css",
})
export class ResumeTemplateList implements OnInit {
    protected readonly templates: WritableSignal<ResumeTemplateType[]> = signal<ResumeTemplateType[]>([]);
    protected readonly isLoading: WritableSignal<boolean> = signal<boolean>(false);
    protected readonly isCreating: WritableSignal<boolean> = signal<boolean>(false);

    private readonly templateService: ResumeTemplateService = inject(ResumeTemplateService);
    private readonly router: Router = inject(Router);

    ngOnInit(): void {
        this.loadTemplates();
    }

    private async loadTemplates(): Promise<void> {
        this.isLoading.set(true);
        try {
            const templates = await this.templateService.getTemplates();
            this.templates.set(templates);
        } finally {
            this.isLoading.set(false);
        }
    }

    protected async onTemplateSelect(template: ResumeTemplateType): Promise<void> {
        if (this.isCreating()) {
            return;
        }

        this.isCreating.set(true);
        try {
            const resume = await this.templateService.createResume(template.id);
            this.router.navigate(["/resume-builder", resume.id], {
                queryParams: { templateId: template.id },
            });
        } catch (error) {
            console.error("Error creating resume:", error);
        } finally {
            this.isCreating.set(false);
        }
    }
}
