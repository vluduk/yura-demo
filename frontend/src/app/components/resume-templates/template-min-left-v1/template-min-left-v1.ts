import { Component } from "@angular/core";
import { BaseTemplate } from "../base-template/base-template";

@Component({
    selector: "app-template-min-left-v1",
    imports: [],
    templateUrl: "./template-min-left-v1.html",
    styleUrl: "./template-min-left-v1.css",
})
export class TemplateMinLeftV1 extends BaseTemplate {
    protected translateProficiency(proficiency: string): string {
        const translations: { [key: string]: string } = {
            'a1': 'Початковий (A1)',
            'a2': 'Елементарний (A2)',
            'b1': 'Середній (B1)',
            'b2': 'Вище середнього (B2)',
            'c1': 'Просунутий (C1)',
            'c2': 'Вільне володіння (C2)',
            'native': 'Рідна мова'
        };
        return translations[proficiency.toLowerCase()] || proficiency.toUpperCase();
    }
}
