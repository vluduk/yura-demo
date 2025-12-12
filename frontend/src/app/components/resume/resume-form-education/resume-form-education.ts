import { Component, input, InputSignal, output, OutputEmitterRef } from "@angular/core";
import { FormsModule } from "@angular/forms";
import { EducationType } from "@shared/types/ResumeDataType";
import { Button } from "@shared/components/button/button";
import { Input } from "@shared/components/input/input";
import { Checkbox } from "@shared/components/checkbox/checkbox";
import { Title } from "@shared/components/title/title";
import { Select } from "@shared/components/select/select";

@Component({
    selector: "app-resume-form-education",
    imports: [FormsModule, Button, Input, Checkbox, Title, Select],
    templateUrl: "./resume-form-education.html",
    styleUrl: "./resume-form-education.css",
})
export class ResumeFormEducation {
    public readonly educations: InputSignal<EducationType[]> = input<EducationType[]>([]);

    public readonly onAdd: OutputEmitterRef<void> = output();
    public readonly onUpdate: OutputEmitterRef<{ id: string; field: keyof EducationType; value: any }> = output();
    public readonly onRemove: OutputEmitterRef<string> = output();

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

    protected addEducation(): void {
        this.onAdd.emit();
    }

    protected updateEducation(id: string, field: keyof EducationType, value: string | boolean | Date | Event): void {
        if (field === 'is_current' && value instanceof Event) {
            const inputElement = value.target as HTMLInputElement;
            value = inputElement.checked;
        }
        this.onUpdate.emit({ id, field, value });
    }

    protected removeEducation(id: string): void {
        this.onRemove.emit(id);
    }

    protected onDatePartChange(eduId: string, field: 'start_date' | 'end_date', type: 'month' | 'year', value: string): void {
        const education = this.educations().find(edu => edu.id === eduId);

        if (education && value) {
            const currentDate = this.parseDate(field === 'start_date' ? education.start_date : education.end_date);

            let month = type === 'month' ? value : currentDate.month;
            let year = type === 'year' ? value : currentDate.year;

            if (!month) {
                month = '01';
            }
            if (!year) {
                year = new Date().getFullYear().toString();
            }

            this.updateDateField(eduId, field, month, year);

            this.autoFillOppositeDate(eduId, field, month, year);
        }
    }

    protected autoFillOppositeDate(eduId: string, changedField: 'start_date' | 'end_date', month: string, year: string): void {
        const education = this.educations().find(edu => edu.id === eduId);
        if (!education) return;

        const oppositeField = changedField === 'start_date' ? 'end_date' : 'start_date';
        const oppositeDate = this.parseDate(changedField === 'start_date' ? education.end_date : education.start_date);
        if (!oppositeDate.month || !oppositeDate.year) {
            if (changedField === 'start_date') {
                const endYear = (parseInt(year)).toString();
                this.updateDateField(eduId, 'end_date', month, endYear);
            } else {
                const startYear = (parseInt(year)).toString();
                this.updateDateField(eduId, 'start_date', month, startYear);
            }
        }
    }

    protected updateDateField(eduId: string, field: 'start_date' | 'end_date', month: string, year: string): void {
        if (month && year) {
            const dateValue = `${year}-${month}`;

            const education = this.educations().find(edu => edu.id === eduId);
            if (education && !this.isValidDate(education, field, dateValue)) {
                return;
            }

            this.updateEducation(eduId, field, dateValue);
        }
    }

    protected isValidDate(education: EducationType, field: 'start_date' | 'end_date', newDateValue: string): boolean {
        const newDate = new Date(newDateValue + '-01');

        if (field === 'end_date') {
            if (education.start_date) {
                const startDate = typeof education.start_date === 'string'
                    ? new Date(education.start_date + '-01')
                    : new Date(education.start_date.getFullYear(), education.start_date.getMonth(), 1);

                return newDate >= startDate;
            }
        } else if (field === 'start_date') {
            if (education.end_date && !education.is_current) {
                const endDate = typeof education.end_date === 'string'
                    ? new Date(education.end_date + '-01')
                    : new Date(education.end_date.getFullYear(), education.end_date.getMonth(), 1);

                return newDate <= endDate;
            }
        }

        return true;
    }

    protected isOptionDisabled(education: EducationType, field: 'start_date' | 'end_date', month: string, year: string): boolean {
        if (!month || !year) return false;

        const testDateValue = `${year}-${month}`;
        return !this.isValidDate(education, field, testDateValue);
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
}
