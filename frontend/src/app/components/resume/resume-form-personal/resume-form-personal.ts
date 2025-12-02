import { Component, input, InputSignal, output, OutputEmitterRef } from "@angular/core";
import { FormsModule } from "@angular/forms";
import { PersonalInfoType } from "@shared/types/ResumeDataType";

@Component({
    selector: "app-resume-form-personal",
    imports: [FormsModule],
    templateUrl: "./resume-form-personal.html",
    styleUrl: "./resume-form-personal.css",
})
export class ResumeFormPersonal {
    public readonly personalInfo: InputSignal<PersonalInfoType | undefined> = input<PersonalInfoType | undefined>();

    public readonly onUpdate: OutputEmitterRef<{ field: keyof PersonalInfoType; value: string }> = output();

    protected updateField(field: keyof PersonalInfoType, event: Event): void {
        const value = (event.target as HTMLInputElement).value;
        this.onUpdate.emit({ field, value });
    }
}
