import { CommonModule } from "@angular/common";
import { Component, input, InputSignal, model, ModelSignal } from "@angular/core";

@Component({
    selector: "ui-textarea",
    imports: [CommonModule],
    templateUrl: "./textarea.html",
    styleUrl: "./textarea.css",
})
export class Textarea {
    public readonly label: InputSignal<string> = input<string>("");
    public readonly placeholder: InputSignal<string> = input<string>("");
    public readonly size: InputSignal<"small" | "large"> = input<"small" | "large">("small");
    public readonly resize: InputSignal<"none" | "horizontal" | "vertical" | "both"> = input<
        "none" | "horizontal" | "vertical" | "both"
    >("none");
    public readonly theme: InputSignal<"default" | "primary"> = input<"default" | "primary">("default");
    public readonly isFullWidth: InputSignal<boolean> = input<boolean>(false);
    public isDisabled: InputSignal<boolean> = input<boolean>(false);

    public value: ModelSignal<string> = model<string>("");

    handleChange(event: Event) {
        const newValue: string = (event.target as HTMLInputElement).value;
        this.value.set(newValue);
    }
}
