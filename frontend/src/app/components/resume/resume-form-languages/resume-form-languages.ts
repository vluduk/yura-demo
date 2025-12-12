import { Component, input, InputSignal, output, OutputEmitterRef, signal, WritableSignal } from "@angular/core";
import { FormsModule } from "@angular/forms";
import { LanguageType } from "@shared/types/ResumeDataType";
import { Button } from "@shared/components/button/button";
import { Input } from "@shared/components/input/input";
import { Title } from "@shared/components/title/title";
import { Select } from "@shared/components/select/select";

@Component({
    selector: "app-resume-form-languages",
    imports: [FormsModule, Button, Input, Title, Select],
    templateUrl: "./resume-form-languages.html",
    styleUrl: "./resume-form-languages.css",
})
export class ResumeFormLanguages {
    public readonly languages: InputSignal<LanguageType[]> = input<LanguageType[]>([]);

    public readonly onAdd: OutputEmitterRef<{ language: string; proficiency: string }> = output();
    public readonly onRemove: OutputEmitterRef<string> = output();

    protected readonly newLang: WritableSignal<string> = signal("");
    protected readonly newProficiency: WritableSignal<string> = signal("b1");

    protected readonly proficiencies: { value: string; label: string }[] = [
        { value: "a1", label: "Початковий (A1)" },
        { value: "a2", label: "Елементарний (A2)" },
        { value: "b1", label: "Середній (B1)" },
        { value: "b2", label: "Вище середнього (B2)" },
        { value: "c1", label: "Просунутий (C1)" },
        { value: "c2", label: "Вільне володіння (C2)" },
        { value: "native", label: "Рідна мова" },
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
