import { Component, input, InputSignal, signal, WritableSignal, output, OutputEmitterRef, effect, inject } from "@angular/core";
import { ResumeDataType } from "@shared/types/ResumeDataType";
import { Button } from "@shared/components/button/button";
import { Textarea } from "@shared/components/textarea/textarea";
import { ResumeService } from "@shared/services/resume.service";

@Component({
    selector: "app-resume-form-summary",
    imports: [Button, Textarea],
    templateUrl: "./resume-form-summary.html",
    styleUrl: "./resume-form-summary.css",
})
export class ResumeFormSummary {
    public readonly data: InputSignal<ResumeDataType> = input.required<ResumeDataType>();
    public readonly onUpdate: OutputEmitterRef<string> = output();

    protected readonly summaryText: WritableSignal<string> = signal<string>("");

    private readonly resumeService: ResumeService = inject(ResumeService);

    constructor() {
        effect(() => {
            const currentData = this.data();
            if (currentData?.personal_info?.summary) {
                this.summaryText.set(currentData.personal_info.summary);
            }
        });
    }

    protected onSummaryChange(value: string): void {
        this.summaryText.set(value);
        this.onUpdate.emit(value);
    }

    protected async generateSummary(): Promise<void> {
        if (!this.resumeService.currentResume()) {
            return;
        }

        const resume: ResumeDataType = this.resumeService.currentResume()!;

        this.onSummaryChange("Автоматично згенероване резюме. Будь ласка, відредагуйте його відповідно до ваших навичок та досвіду.");

        const context: any = {};

        if (resume.personal_info) {
            context['personal_info'] = resume.personal_info;
        }
        if (resume.experience) {
            context['experience'] = resume.experience;
        }
        if (resume.education) {
            context['education'] = resume.education;
        }
        if (resume.skills) {
            context['skills'] = resume.skills;
        }
        if (resume.languages) {
            context['languages'] = resume.languages;
        }
        if (resume.extra_activities) {
            context['extra_activities'] = resume.extra_activities;
        }

        const content = await this.resumeService.generateAIContent(resume.id, 'summary', context);

        if (content) {
            this.onSummaryChange(content);
        }
    }
}
