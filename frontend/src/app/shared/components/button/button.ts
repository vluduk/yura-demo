import { CommonModule } from "@angular/common";
import { Component, input, InputSignal, output, OutputEmitterRef } from "@angular/core";

@Component({
    selector: "ui-button",
    imports: [CommonModule],
    templateUrl: "./button.html",
    styleUrl: "./button.css",
})
export class Button {
    public readonly label: InputSignal<string> = input<string>("");
    public readonly icon: InputSignal<string> = input<string>("");
    public readonly size: InputSignal<"small" | "medium" | "large"> = input<"small" | "medium" | "large">("small");
    public readonly type: InputSignal<"primary" | "primary-line" | "secondary" | "icon"> = input<
        "primary" | "primary-line" | "secondary" | "icon"
    >("primary");
    public readonly align: InputSignal<"left" | "center"> = input<"left" | "center">("center");
    public readonly isDisabled: InputSignal<boolean> = input<boolean>(false);
    public readonly isFullWidth: InputSignal<boolean> = input<boolean>(false);
    public readonly isLoading: InputSignal<boolean> = input<boolean>(false);

    public readonly click: OutputEmitterRef<MouseEvent> = output<MouseEvent>();

    handleClick(event: MouseEvent): void {
        event.preventDefault();
        event.stopPropagation();
        this.click.emit(event);
    }
}
