import { Component, input, InputSignal } from "@angular/core";
import { RouterLink } from "@angular/router";

@Component({
    selector: "ui-logo",
    imports: [RouterLink],
    templateUrl: "./logo.html",
    styleUrl: "./logo.css",
})
export class Logo {
    public readonly size: InputSignal<"small" | "large"> = input<"small" | "large">("large");
}
