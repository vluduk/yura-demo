import { Component, input, InputSignal } from "@angular/core";
import { ResumeDataType } from "@shared/types/ResumeDataType";
import { IResumeTemplate } from "@shared/types/ResumeModel";
import { MarkdownModule } from "ngx-markdown";

@Component({
    selector: "app-base-template",
    imports: [MarkdownModule],
    template: "",
})
export abstract class BaseTemplate implements IResumeTemplate {
    public readonly data: InputSignal<ResumeDataType> = input.required<ResumeDataType>();
    public readonly scale: InputSignal<number> = input.required<number>();

    ngAfterContentInit(): void {
        console.log(this.data());
    }

    protected formatDate(date: Date | string | undefined): string {
        if (!date) return "";

        if (date instanceof Date) {
            const year = date.getFullYear();
            const month = String(date.getMonth() + 1).padStart(2, "0");
            return `${year}-${month}`;
        }

        return date.toString();
    }
}
