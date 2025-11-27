import { Component } from "@angular/core";
import { RouterOutlet } from "@angular/router";
import { Footer } from "@components/footer/footer";
import { Header } from "@components/header/header";

@Component({
    selector: "app-layout-main",
    imports: [RouterOutlet, Header, Footer],
    templateUrl: "./layout-main.html",
    styleUrl: "./layout-main.css",
})
export class LayoutMain {}
