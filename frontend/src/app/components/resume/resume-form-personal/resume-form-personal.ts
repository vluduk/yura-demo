import { Component, input, InputSignal, output, OutputEmitterRef, inject } from "@angular/core";
import { FormsModule } from "@angular/forms";
import { PersonalInfoType } from "@shared/types/ResumeDataType";
import { ResumeService } from "@shared/services/resume.service";
import { Button } from "@shared/components/button/button";

@Component({
    selector: "app-resume-form-personal",
    imports: [FormsModule, Button],
    templateUrl: "./resume-form-personal.html",
    styleUrl: "./resume-form-personal.css",
})
export class ResumeFormPersonal {
    private readonly resumeService = inject(ResumeService);
    public readonly personalInfo: InputSignal<PersonalInfoType | undefined> = input<PersonalInfoType | undefined>();

    public readonly onUpdate: OutputEmitterRef<{ field: keyof PersonalInfoType; value: string }> = output();

    protected updateField(field: keyof PersonalInfoType, event: Event): void {
        const value = (event.target as HTMLInputElement).value;
        this.onUpdate.emit({ field, value });
    }

    protected async generateSummary(): Promise<void> {
        const resume = this.resumeService.currentResume();
        if (!resume) return;

        const content = await this.resumeService.generateAIContent(resume.id, 'summary');
        if (content) {
            this.onUpdate.emit({ field: 'summary', value: content });
        }
    }
}
