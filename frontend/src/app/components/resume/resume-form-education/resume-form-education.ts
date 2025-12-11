import { Component, input, InputSignal, output, OutputEmitterRef } from "@angular/core";
import { FormsModule } from "@angular/forms";
import { EducationType } from "@shared/types/ResumeDataType";
import { Button } from "@shared/components/button/button";
import { Input } from "@shared/components/input/input";
import { Checkbox } from "@shared/components/checkbox/checkbox";

@Component({
    selector: "app-resume-form-education",
    imports: [FormsModule, Button, Input, Checkbox],
    templateUrl: "./resume-form-education.html",
    styleUrl: "./resume-form-education.css",
})
export class ResumeFormEducation {
    public readonly educations: InputSignal<EducationType[]> = input<EducationType[]>([]);

    public readonly onAdd: OutputEmitterRef<void> = output();
    public readonly onUpdate: OutputEmitterRef<{ id: string; field: keyof EducationType; value: any }> = output();
    public readonly onRemove: OutputEmitterRef<string> = output();

    protected addEducation(): void {
        this.onAdd.emit();
    }

    protected updateEducation(id: string, field: keyof EducationType, value: string | number | boolean): void {
        this.onUpdate.emit({ id, field, value });
    }

    protected updateCheckboxEducation(id: string, field: keyof EducationType, event: Event): void {
        const target = event.target as HTMLInputElement;
        const value = target.checked;
        this.onUpdate.emit({ id, field, value });
    }

    protected removeEducation(id: string): void {
        this.onRemove.emit(id);
    }
}
