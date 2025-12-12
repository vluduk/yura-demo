import { Component, input, InputSignal, signal, WritableSignal, output, OutputEmitterRef, effect } from "@angular/core";
import { ResumeDataType } from "@shared/types/ResumeDataType";
import { Button } from "@shared/components/button/button";
import { Textarea } from "@shared/components/textarea/textarea";

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

    protected generateSummary(): void {
        this.onSummaryChange("Автоматично згенероване резюме. Будь ласка, відредагуйте його відповідно до ваших навичок та досвіду.");
    }
}
