import { Component, input, InputSignal, output, OutputEmitterRef, signal, WritableSignal } from "@angular/core";
import { FormsModule } from "@angular/forms";
import { SkillType } from "@shared/types/ResumeDataType";
import { Button } from "@shared/components/button/button";
import { Title } from "@shared/components/title/title";
import { Select } from "@shared/components/select/select";
import { Input } from "@shared/components/input/input";

@Component({
    selector: "app-resume-form-skills",
    imports: [FormsModule, Button, Title, Select, Input],
    templateUrl: "./resume-form-skills.html",
    styleUrl: "./resume-form-skills.css",
})
export class ResumeFormSkills {
    public readonly skills: InputSignal<SkillType[]> = input<SkillType[]>([]);

    public readonly onAdd: OutputEmitterRef<{ name: string; level: string }> = output();
    public readonly onRemove: OutputEmitterRef<string> = output();

    protected readonly newSkill: WritableSignal<string> = signal("");
    protected readonly newLevel: WritableSignal<string> = signal("intermediate");

    protected readonly levels: { value: string; label: string }[] = [
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
