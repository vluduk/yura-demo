import { CommonModule } from "@angular/common";
import { Component, input, InputSignal, model, ModelSignal } from "@angular/core";

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
    public isDisabled: InputSignal<boolean> = input<boolean>(false);
    public isFullWidth: InputSignal<boolean> = input<boolean>(false);

    public value: ModelSignal<string> = model<string>("");

    handleChange(event: Event): void {
        const newValue: string = (event.target as HTMLSelectElement).value;
        this.value.set(newValue);
    }
}
