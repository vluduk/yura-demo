import { Component, inject, input, InputSignal, output, OutputEmitterRef } from "@angular/core";
import { FormsModule } from "@angular/forms";
import { ExtraActivityType, ResumeDataType } from "@shared/types/ResumeDataType";
import { Button } from "@shared/components/button/button";
import { Input } from "@shared/components/input/input";
import { Select } from "@shared/components/select/select";
import { ResumeService } from "@shared/services/resume.service";
import { Checkbox } from "@shared/components/checkbox/checkbox";
import { Textarea } from "@shared/components/textarea/textarea";
import { Title } from "@shared/components/title/title";

@Component({
    selector: "app-resume-form-extra-activities",
    imports: [FormsModule, Button, Input, Select, Checkbox, Textarea, Title],
    templateUrl: "./resume-form-extra-activities.html",
    styleUrl: "./resume-form-extra-activities.css",
})
export class ResumeFormExtraActivities {
    public readonly activities: InputSignal<ExtraActivityType[]> = input<ExtraActivityType[]>([]);

    public readonly onAdd: OutputEmitterRef<void> = output();
    public readonly onUpdate: OutputEmitterRef<{ id: string; field: keyof ExtraActivityType; value: any }> = output();
    public readonly onRemove: OutputEmitterRef<string> = output();

    private readonly resumeService = inject(ResumeService);

    protected readonly months = [
        { value: '01', label: 'Січень' },
        { value: '02', label: 'Лютий' },
        { value: '03', label: 'Березень' },
        { value: '04', label: 'Квітень' },
        { value: '05', label: 'Травень' },
        { value: '06', label: 'Червень' },
        { value: '07', label: 'Липень' },
        { value: '08', label: 'Серпень' },
        { value: '09', label: 'Вересень' },
        { value: '10', label: 'Жовтень' },
        { value: '11', label: 'Листопад' },
        { value: '12', label: 'Грудень' }
    ];

    protected readonly years = Array.from({ length: 50 }, (_, i) => {
        const year = new Date().getFullYear() - i;
        return year.toString();
    });

    protected addActivity(): void {
        this.onAdd.emit();
    }

    protected updateActivity(id: string, field: keyof ExtraActivityType, value: string | boolean | Date | Event): void {
        if (field === 'is_current' && value instanceof Event) {
            const inputElement = value.target as HTMLInputElement;
            value = inputElement.checked;
        }
        this.onUpdate.emit({ id, field, value });
    }

    protected removeActivity(id: string): void {
        this.onRemove.emit(id);
    }

    protected onDatePartChange(actId: string, field: 'start_date' | 'end_date', type: 'month' | 'year', value: string): void {
        const activity = this.activities().find(act => act.id === actId);

        if (activity && value) {
            const currentDate = this.parseDate(field === 'start_date' ? activity.start_date : activity.end_date);

            let month = type === 'month' ? value : currentDate.month;
            let year = type === 'year' ? value : currentDate.year;

            if (!month) {
                month = '01';
            }
            if (!year) {
                year = new Date().getFullYear().toString();
            }

            this.updateDateField(actId, field, month, year);

            this.autoFillOppositeDate(actId, field, month, year);
        }
    }

    protected autoFillOppositeDate(actId: string, changedField: 'start_date' | 'end_date', month: string, year: string): void {
        const activity = this.activities().find(act => act.id === actId);
        if (!activity) return;

        const oppositeField = changedField === 'start_date' ? 'end_date' : 'start_date';
        const oppositeDate = this.parseDate(changedField === 'start_date' ? activity.end_date : activity.start_date);
        if (!oppositeDate.month || !oppositeDate.year) {
            if (changedField === 'start_date') {
                const endYear = (parseInt(year)).toString();
                this.updateDateField(actId, 'end_date', month, endYear);
            } else {
                const startYear = (parseInt(year)).toString();
                this.updateDateField(actId, 'start_date', month, startYear);
            }
        }
    }

    protected updateDateField(actId: string, field: 'start_date' | 'end_date', month: string, year: string): void {
        if (month && year) {
            const dateValue = `${year}-${month}`;

            const activity = this.activities().find(act => act.id === actId);
            if (activity && !this.isValidDate(activity, field, dateValue)) {
                return;
            }

            this.updateActivity(actId, field, dateValue);
        }
    }

    protected isValidDate(activity: ExtraActivityType, field: 'start_date' | 'end_date', newDateValue: string): boolean {
        const newDate = new Date(newDateValue + '-01');

        if (field === 'end_date') {
            if (activity.start_date) {
                const startDate = typeof activity.start_date === 'string'
                    ? new Date(activity.start_date + '-01')
                    : new Date(activity.start_date.getFullYear(), activity.start_date.getMonth(), 1);

                return newDate >= startDate;
            }
        } else if (field === 'start_date') {
            if (activity.end_date && !activity.is_current) {
                const endDate = typeof activity.end_date === 'string'
                    ? new Date(activity.end_date + '-01')
                    : new Date(activity.end_date.getFullYear(), activity.end_date.getMonth(), 1);

                return newDate <= endDate;
            }
        }

        return true;
    }

    protected isOptionDisabled(activity: ExtraActivityType, field: 'start_date' | 'end_date', month: string, year: string): boolean {
        if (!month || !year) return false;

        const testDateValue = `${year}-${month}`;
        return !this.isValidDate(activity, field, testDateValue);
    }

    protected parseDate(dateValue: string | Date | undefined): { month: string, year: string } {
        if (!dateValue) return { month: '', year: '' };

        let dateString: string;
        if (dateValue instanceof Date) {
            const year = dateValue.getFullYear();
            const month = (dateValue.getMonth() + 1).toString().padStart(2, '0');
            dateString = `${year}-${month}`;
        } else {
            dateString = dateValue.toString();
        }

        const [year, month] = dateString.split('-');
        return { month: month || '', year: year || '' };
    }

    protected async generateDescription(actId: string): Promise<void> {
        if (!this.resumeService.currentResume()) {
            return;
        }

        const resume: ResumeDataType = this.resumeService.currentResume()!;

        const activity: ExtraActivityType = this.resumeService.currentResume()?.extra_activities!.find(act => act.id === actId)!;

        const content = await this.resumeService.generateAIContent(resume.id, 'description', {
            activity_title: activity.title,
            activity_organization: activity.organization,
            activity_description: activity.description || '',
        });

        if (content) {
            this.onUpdate.emit({ id: resume.id, field: 'description', value: content });
        }
    }
}
