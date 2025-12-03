import { Component, input, InputSignal, output, OutputEmitterRef } from "@angular/core";
import { FormsModule } from "@angular/forms";
import { ExtraActivityType } from "@shared/types/ResumeDataType";
import { Button } from "@shared/components/button/button";

@Component({
    selector: "app-resume-form-extra-activities",
    imports: [FormsModule, Button],
    templateUrl: "./resume-form-extra-activities.html",
    // Inline minimal styles to avoid build errors when external file is not found
    styles: [`.form-extra-activities { padding: 12px; }
    .form__header { display:flex; justify-content:space-between; align-items:center; margin-bottom:8px; }
    .form__title { margin:0; font-size:16px; }
    .activity-item { border:1px solid #e6e6e6; padding:10px; margin-bottom:8px; border-radius:6px; }
    .form__row { display:flex; gap:12px; }
    .form__field { flex:1; display:flex; flex-direction:column; }
    .field__label { font-size:12px; margin-bottom:4px; }
    .field__input, .field__textarea { padding:6px 8px; border:1px solid #ccc; border-radius:4px; }
    .form__empty { color:#666; }
    .item__header { display:flex; justify-content:space-between; align-items:center; }
    .item__remove { background:none; border:none; cursor:pointer; color:#c00; }`],
})
export class ResumeFormExtraActivities {
    public readonly activities: InputSignal<ExtraActivityType[]> = input<ExtraActivityType[]>([]);

    public readonly onAdd: OutputEmitterRef<void> = output();
    public readonly onUpdate: OutputEmitterRef<{ id: string; field: keyof ExtraActivityType; value: any }> = output();
    public readonly onRemove: OutputEmitterRef<string> = output();

    protected addActivity(): void {
        this.onAdd.emit();
    }

    protected updateActivity(id: string, field: keyof ExtraActivityType, event: Event): void {
        const target = event.target as HTMLInputElement;
        const value = target.type === "checkbox" ? target.checked : target.value;
        this.onUpdate.emit({ id, field, value });
    }

    protected removeActivity(id: string): void {
        this.onRemove.emit(id);
    }
}
