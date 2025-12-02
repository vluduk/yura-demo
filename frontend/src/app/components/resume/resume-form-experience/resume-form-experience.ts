import { Component, input, InputSignal, output, OutputEmitterRef } from "@angular/core";
import { FormsModule } from "@angular/forms";
import { ExperienceType } from "@shared/types/ResumeDataType";
import { Button } from "@shared/components/button/button";

@Component({
    selector: "app-resume-form-experience",
    imports: [FormsModule, Button],
    templateUrl: "./resume-form-experience.html",
    styleUrl: "./resume-form-experience.css",
})
export class ResumeFormExperience {
    public readonly experiences: InputSignal<ExperienceType[]> = input<ExperienceType[]>([]);

    public readonly onAdd: OutputEmitterRef<void> = output();
    public readonly onUpdate: OutputEmitterRef<{ id: string; field: keyof ExperienceType; value: any }> = output();
    public readonly onRemove: OutputEmitterRef<string> = output();

    protected addExperience(): void {
        this.onAdd.emit();
    }

    protected updateExperience(id: string, field: keyof ExperienceType, event: Event): void {
        const target = event.target as HTMLInputElement;
        const value = target.type === "checkbox" ? target.checked : target.value;
        this.onUpdate.emit({ id, field, value });
    }

    protected removeExperience(id: string): void {
        this.onRemove.emit(id);
    }
}
