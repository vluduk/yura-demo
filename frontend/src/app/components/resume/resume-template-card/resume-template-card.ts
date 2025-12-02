import { Component, input, InputSignal, output, OutputEmitterRef } from "@angular/core";
import { ResumeTemplateType } from "@shared/types/ResumeTemplateType";

@Component({
    selector: "app-resume-template-card",
    imports: [],
    templateUrl: "./resume-template-card.html",
    styleUrl: "./resume-template-card.css",
})
export class ResumeTemplateCard {
    public readonly template: InputSignal<ResumeTemplateType> = input.required<ResumeTemplateType>();

    public readonly onSelect: OutputEmitterRef<ResumeTemplateType> = output<ResumeTemplateType>();

    protected handleSelect(): void {
        this.onSelect.emit(this.template());
    }
}
