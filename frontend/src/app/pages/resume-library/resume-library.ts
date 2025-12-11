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
    templateUrl: "./resume-library.html",
    styleUrls: ["./resume-library.css"],
})
export class ResumeLibraryComponent implements OnInit {
    private resumeService = inject(ResumeService);
    private router = inject(Router);

    protected resumes: WritableSignal<ResumeDataType[]> = signal<ResumeDataType[]>([]);
    protected isLoading: WritableSignal<boolean> = this.resumeService.isLoading;

    ngOnInit(): void {
        this.loadResumes();
    }

    private async loadResumes(): Promise<void> {
        const list = await this.resumeService.getResumes();
        this.resumes.set(list);
    }

    protected createNew(): void {
        // Navigate to resume builder with 'new' or handling creation
        // Usually builder is at /resume-builder or similar based on existing routes?
        // Checking routes file might be needed, but assuming /resume based on typical patterns or 'resume-builder'
        this.router.navigate(["/sub-pages/resume-builder"]);
    }

    protected viewResume(id: string): void {
        this.router.navigate(["/sub-pages/resume-builder"], { queryParams: { id } });
    }

    protected getInitials(resume: ResumeDataType): string {
        const first = resume.personal_info?.first_name?.charAt(0) || "";
        const last = resume.personal_info?.last_name?.charAt(0) || "";
        return (first + last).toUpperCase() || "R";
    }

    protected formatDate(dateStr?: string | Date): string {
        if (!dateStr) return "";
        return new Date(dateStr).toLocaleDateString("uk-UA", {
            day: "numeric",
            month: "short",
            year: "numeric",
        });
    }
}
