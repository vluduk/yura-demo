import { Component, input, InputSignal, output, OutputEmitterRef, signal, WritableSignal } from "@angular/core";
import { FormsModule } from "@angular/forms";
import { SkillType } from "@shared/types/ResumeDataType";
import { Button } from "@shared/components/button/button";

@Component({
    selector: "app-resume-form-skills",
    imports: [FormsModule, Button],
    templateUrl: "./resume-form-skills.html",
    styleUrl: "./resume-form-skills.css",
})
export class ResumeFormSkills {
    public readonly skills: InputSignal<SkillType[]> = input<SkillType[]>([]);

    public readonly onAdd: OutputEmitterRef<{ name: string; level: SkillType["level"] }> = output();
    public readonly onRemove: OutputEmitterRef<string> = output();

    protected readonly newSkill: WritableSignal<string> = signal("");
    protected readonly newLevel: WritableSignal<SkillType["level"]> = signal("intermediate");

    protected readonly levels: { value: SkillType["level"]; label: string }[] = [
        { value: "beginner", label: "Початковий" },
        { value: "intermediate", label: "Середній" },
        { value: "advanced", label: "Просунутий" },
        { value: "expert", label: "Експерт" },
    ];

    protected addSkill(): void {
        if (this.newSkill().trim()) {
            this.onAdd.emit({ name: this.newSkill().trim(), level: this.newLevel() });
            this.newSkill.set("");
        }
    }

    protected removeSkill(id: string): void {
        this.onRemove.emit(id);
    }
}
