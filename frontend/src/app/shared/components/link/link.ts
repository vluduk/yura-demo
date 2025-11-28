import { CommonModule } from "@angular/common";
import { Component, input, InputSignal } from "@angular/core";
import { RouterLink, UrlTree } from "@angular/router";

@Component({
    selector: "ui-link",
    imports: [CommonModule, RouterLink],
    templateUrl: "./link.html",
    styleUrl: "./link.css",
})
export class Link {
    public readonly path: InputSignal<string> = input<string>("");
    public readonly routerLink: InputSignal<string | any[] | UrlTree> = input<string | any[] | UrlTree>("");
    public readonly label: InputSignal<string> = input<string>("");
    public readonly icon: InputSignal<string> = input<string>("");
    public readonly type: InputSignal<"primary" | "primary-line" | "light" | "light-line" | "light-clear"> = input<
        "primary" | "primary-line" | "light" | "light-line" | "light-clear"
    >("primary");
    public readonly isDisabled: InputSignal<boolean> = input<boolean>(false);
    public readonly isFullWidth: InputSignal<boolean> = input<boolean>(false);
    public readonly target: InputSignal<"_self" | "_blank"> = input<"_self" | "_blank">("_self");
}
