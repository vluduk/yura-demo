import { Component, input, InputSignal, signal, WritableSignal } from "@angular/core";
import {
    ResumeDataType,
    ExperienceType,
    EducationType,
    SkillType,
    PersonalInfoType,
} from "@shared/types/ResumeDataType";
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

    protected readonly summaryText: WritableSignal<string> = signal<string>("");

    protected generateSummary(): void {}
}
