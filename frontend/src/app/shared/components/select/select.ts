import { CommonModule } from "@angular/common";
import { Component, input, InputSignal, model, ModelSignal, output, OutputEmitterRef } from "@angular/core";

@Component({
    selector: "ui-select",
    imports: [CommonModule],
    templateUrl: "./select.html",
    styleUrl: "./select.css",
})
export class Select {
    public readonly label: InputSignal<string> = input<string>("");
    public readonly size: InputSignal<"small" | "large"> = input<"small" | "large">("small");
    public readonly theme: InputSignal<"primary"> = input<"primary">("primary");
    public readonly isDisabled: InputSignal<boolean> = input<boolean>(false);
    public readonly isFullWidth: InputSignal<boolean> = input<boolean>(false);

    public readonly value: ModelSignal<string> = model<string>("");
    public readonly valueChange: OutputEmitterRef<string> = output<string>();

    handleChange(event: Event): void {
        const newValue: string = (event.target as HTMLSelectElement).value;
        console.log("ui-select change detected:", newValue);
        this.value.set(newValue);
        this.valueChange.emit(newValue);
    }
}
