import { Type } from "@angular/core";
import { TemplateMinLeftV1 } from "@components/resume-templates/template-min-left-v1/template-min-left-v1";
import { IResumeTemplate } from "./ResumeModel";
import { TemplateMinTopV1 } from "@components/resume-templates/template-min-top-v1/template-min-top-v1";

export type ResumeTemplateType = {
    id: string;
    name: string;
    preview_image: string;
    component: Type<IResumeTemplate>;
};

export const TEMPLATES: Record<string, ResumeTemplateType> = {
    "min-left-v1": {
        id: "min-left-v1",
        name: "Мінімалістичний (ліва панель)",
        preview_image: "https://cdn.example.com/templates/min-left-v1/preview.jpg",
        component: TemplateMinLeftV1,
    },
    "min-top-v1": {
        id: "min-top-v1",
        name: "Мінімалістичний (верхня панель)",
        preview_image: "https://cdn.example.com/templates/min-top-v1/preview.jpg",
        component: TemplateMinTopV1,
    },
};
