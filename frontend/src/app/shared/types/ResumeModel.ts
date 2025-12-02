import { InputSignal } from "@angular/core";
import { ResumeDataType } from "./ResumeDataType";

export interface IResumeTemplate {
    data: InputSignal<ResumeDataType>;
    scale: InputSignal<number>;
}
