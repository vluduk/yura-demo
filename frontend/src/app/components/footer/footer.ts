import { Component } from "@angular/core";
import { Logo } from "@shared/components/logo/logo";
import { Link } from "@shared/components/link/link";

@Component({
    selector: "app-footer",
    imports: [Logo, Link],
    templateUrl: "./footer.html",
    styleUrl: "./footer.css",
})
export class Footer {}
