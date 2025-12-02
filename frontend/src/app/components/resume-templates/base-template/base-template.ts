import { Component, input, InputSignal } from "@angular/core";
import { ResumeDataType } from "@shared/types/ResumeDataType";
import { IResumeTemplate } from "@shared/types/ResumeModel";

@Component({
    selector: "app-base-template",
    imports: [],
    template: "",
})
export abstract class BaseTemplate implements IResumeTemplate {
    public readonly data: InputSignal<ResumeDataType> = input.required<ResumeDataType>();
    public readonly scale: InputSignal<number> = input.required<number>();

    ngAfterContentInit(): void {
        console.log(this.data());
    }
}
