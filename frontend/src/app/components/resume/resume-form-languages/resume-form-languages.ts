import { Component, input, InputSignal, output, OutputEmitterRef, signal, WritableSignal } from "@angular/core";
import { FormsModule } from "@angular/forms";
import { LanguageType } from "@shared/types/ResumeDataType";
import { Button } from "@shared/components/button/button";

@Component({
    selector: "app-resume-form-languages",
    imports: [FormsModule, Button],
    templateUrl: "./resume-form-languages.html",
    styleUrl: "./resume-form-languages.css",
})
export class ResumeFormLanguages {
    public readonly languages: InputSignal<LanguageType[]> = input<LanguageType[]>([]);

    public readonly onAdd: OutputEmitterRef<{ language: string; proficiency: LanguageType["proficiency"] }> = output();
    public readonly onRemove: OutputEmitterRef<string> = output();

    protected readonly newLang: WritableSignal<string> = signal("");
    protected readonly newProficiency: WritableSignal<LanguageType["proficiency"]> = signal("b1");

    protected readonly proficiencies: { value: LanguageType["proficiency"]; label: string }[] = [
        { value: "a1", label: "A1" },
        { value: "a2", label: "A2" },
        { value: "b1", label: "B1" },
        { value: "b2", label: "B2" },
        { value: "c1", label: "C1" },
        { value: "c2", label: "C2" },
        { value: "native", label: "Рідна" },
    ];

    protected addLanguage(): void {
        if (this.newLang().trim()) {
            this.onAdd.emit({ language: this.newLang().trim(), proficiency: this.newProficiency() });
            this.newLang.set("");
        }
    }

    protected removeLanguage(id: string): void {
        this.onRemove.emit(id);
    }
}
