import { CommonModule } from "@angular/common";
import { Component, input, InputSignal } from "@angular/core";

@Component({
    selector: "ui-title",
    imports: [CommonModule],
    templateUrl: "./title.html",
    styleUrl: "./title.css",
})
export class Title {
    public readonly title: InputSignal<string> = input<string>("");
    public readonly size: InputSignal<"small" | "medium" | "large"> = input<"small" | "medium" | "large">("small");
    public readonly theme: InputSignal<"primary" | "secondary"> = input<"primary" | "secondary">("primary");
    public readonly align: InputSignal<"left" | "center" | "right"> = input<"left" | "center" | "right">("left");
}
