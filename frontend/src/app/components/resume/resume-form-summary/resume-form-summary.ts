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
    protected readonly isGenerating: WritableSignal<boolean> = signal<boolean>(false);

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

        this.isGenerating.set(true);
        const resume: ResumeDataType = this.resumeService.currentResume()!;

        try {
            // Prepare context for AI
            const context: any = {};
            if (resume.experience) {
                context['experience'] = resume.experience;
            }
            // Add other fields if needed by backend
            
            const summary = await this.resumeService.generateSummary(context);
            this.onSummaryChange(summary);
        } catch (error) {
            console.error("Failed to generate summary", error);
            // Optionally show error notification
        } finally {
            this.isGenerating.set(false);
        }
    }
}
