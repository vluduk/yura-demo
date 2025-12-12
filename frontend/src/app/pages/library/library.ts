import { Component, OnInit, inject, signal, WritableSignal } from "@angular/core";
import { CommonModule } from "@angular/common";
import { Router, RouterModule } from "@angular/router";
import { ResumeService } from "@shared/services/resume.service";
import { ResumeDataType } from "@shared/types/ResumeDataType";
import { Button } from "@shared/components/button/button";

@Component({
    selector: "app-resume-library",
    standalone: true,
    imports: [CommonModule, RouterModule, Button],
    templateUrl: "./library.html",
    styleUrl: "./library.css",
})
export class Library implements OnInit {
    private readonly resumeService = inject(ResumeService);
    private readonly router = inject(Router);

    protected readonly resumes: WritableSignal<ResumeDataType[]> = signal<ResumeDataType[]>([]);

    ngOnInit(): void {
        this.loadResumes();
    }

    private async loadResumes(): Promise<void> {
        // const list = await this.resumeService.getResumes();
        // this.resumes.set(list);
    }

    protected createNew(): void {
        this.router.navigate(["/resume-templates"]);
    }

    protected viewResume(id: string): void {
        this.router.navigate(["/resume-builder"], { queryParams: { resumeId: id } });
    }

    protected getInitials(resume: ResumeDataType): string {
        const first = resume.personal_info?.first_name?.charAt(0) || "";
        const last = resume.personal_info?.last_name?.charAt(0) || "";
        return (first + last).toUpperCase() || "R";
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
}
