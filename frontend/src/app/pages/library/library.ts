import { Component, OnInit, inject, signal, WritableSignal, Signal, computed } from "@angular/core";
import { CommonModule } from "@angular/common";
import { Router, RouterModule } from "@angular/router";
import { ResumeService } from "@shared/services/resume.service";
import { ResumeDataType } from "@shared/types/ResumeDataType";
import { Button } from "@shared/components/button/button";
import { TEMPLATES } from "@shared/types/ResumeTemplateType";
import { Title } from "@shared/components/title/title";
import { Input } from "@shared/components/input/input";

@Component({
    selector: "app-resume-library",
    standalone: true,
    imports: [CommonModule, RouterModule, Button, Title, Input],
    templateUrl: "./library.html",
    styleUrl: "./library.css",
})
export class Library implements OnInit {
    protected readonly resumes: WritableSignal<ResumeDataType[]> = signal<ResumeDataType[]>([]);
    protected readonly isLoading: Signal<boolean> = computed(() => this.resumeService.isLoading());

    protected readonly titleEditingId: WritableSignal<string> = signal<string>("");

    private debounceTimeout: ReturnType<typeof setTimeout> | null = null;

    private readonly resumeService: ResumeService = inject(ResumeService);
    private readonly router: Router = inject(Router);

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
        const resume = this.resumes().find((r) => r.id === id);
        if (resume) {
            this.resumeService.currentResume.set(resume);
        }
        this.router.navigate(["/resume-builder", id], { queryParams: { templateId: this.getTemplateId(id) } });
    }

    protected getTemplateName(templateId: string): string {
        return TEMPLATES[templateId]?.name || "Невідомий шаблон";
    }

    protected getTemplateId(resumeId: string): string {
        const resume = this.resumes().find((r) => r.id === resumeId);
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

    protected toggleTitleEditing(resumeId: string): void {
        this.titleEditingId.set(resumeId === this.titleEditingId() ? "" : resumeId);
    }

    protected async updateTitle(resumeId: string, newTitle: string): Promise<void> {
        if (this.debounceTimeout) {
            clearTimeout(this.debounceTimeout);
        }

        this.debounceTimeout = setTimeout(async () => {
            this.resumes.update((resumes) => resumes.map((r) => (r.id === resumeId ? { ...r, title: newTitle } : r)));

            try {
                await this.resumeService.saveResume(this.resumes().find((r) => r.id === resumeId)!);
            } catch (error) {
                console.error("Failed to save resume", error);
            }
        }, 500);
    }
}
