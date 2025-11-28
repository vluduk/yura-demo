import { Component } from "@angular/core";
import { RouterOutlet } from "@angular/router";
import { Title } from "@shared/components/title/title";

@Component({
    selector: "app-layout-auth",
    imports: [RouterOutlet, Title],
    templateUrl: "./layout-auth.html",
    styleUrl: "./layout-auth.css",
})
export class LayoutAuth {}
