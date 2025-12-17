import { Component } from "@angular/core";
import { BaseTemplate } from "../base-template/base-template";
import { MarkdownModule } from "ngx-markdown";

@Component({
    selector: "app-template-min-top-v1",
    imports: [MarkdownModule],
    templateUrl: "./template-min-top-v1.html",
    styleUrl: "./template-min-top-v1.css",
})
export class TemplateMinTopV1 extends BaseTemplate {}
