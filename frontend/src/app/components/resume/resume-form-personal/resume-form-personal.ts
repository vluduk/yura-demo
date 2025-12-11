import { Component, input, InputSignal, output, OutputEmitterRef } from "@angular/core";
import { FormsModule } from "@angular/forms";
import { PersonalInfoType } from "@shared/types/ResumeDataType";
import { Input } from "@shared/components/input/input";
import { Title } from "@shared/components/title/title";

@Component({
    selector: "app-resume-form-personal",
    imports: [FormsModule, Input, Title],
    templateUrl: "./resume-form-personal.html",
    styleUrl: "./resume-form-personal.css",
})
export class ResumeFormPersonal {
    public readonly personalInfo: InputSignal<PersonalInfoType | undefined> = input<PersonalInfoType | undefined>();

    public readonly onUpdate: OutputEmitterRef<{ field: keyof PersonalInfoType; value: string }> = output();

    protected updateField(field: keyof PersonalInfoType, value: string | number): void {
        this.onUpdate.emit({ field, value: String(value) });
    }
}
