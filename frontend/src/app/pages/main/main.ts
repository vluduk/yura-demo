import { Component } from "@angular/core";
import { Title } from "@shared/components/title/title";
import { Button } from "@shared/components/button/button";

@Component({
    selector: "app-main",
    imports: [Title, Button],
    templateUrl: "./main.html",
    styleUrl: "./main.css",
})
export class Main {}
