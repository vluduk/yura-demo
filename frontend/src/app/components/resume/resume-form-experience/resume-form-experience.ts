import { Component, computed, inject, input, InputSignal, output, OutputEmitterRef, Signal } from "@angular/core";
import { FormsModule } from "@angular/forms";
import { CommonModule, DatePipe } from "@angular/common";
import { ExperienceType } from "@shared/types/ResumeDataType";
import { Button } from "@shared/components/button/button";
import { Title } from "@shared/components/title/title";
import { Input } from "@shared/components/input/input";
import { Checkbox } from "@shared/components/checkbox/checkbox";
import { Textarea } from "@shared/components/textarea/textarea";
import { ResumeService } from "@shared/services/resume.service";
import { Select } from "@shared/components/select/select";

@Component({
    selector: "app-resume-form-experience",
    imports: [FormsModule, CommonModule, Button, Title, Input, Checkbox, Textarea, Select],
    templateUrl: "./resume-form-experience.html",
    styleUrl: "./resume-form-experience.css",
})
export class ResumeFormExperience {
    public readonly experiences: InputSignal<ExperienceType[]> = input<ExperienceType[]>([]);

    public readonly onAdd: OutputEmitterRef<void> = output();
    public readonly onUpdate: OutputEmitterRef<{ id: string; field: keyof ExperienceType; value: string | boolean | Date | Event }> = output();
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

    protected addExperience(): void {
        this.onAdd.emit();
    }

    protected updateExperience(id: string, field: keyof ExperienceType, value: string | boolean | Date | Event): void {
        if (field === 'is_current' && value instanceof Event) {
            const inputElement = value.target as HTMLInputElement;
            value = inputElement.checked;
        }
        this.onUpdate.emit({ id, field, value });
    }

    protected onDatePartChange(expId: string, field: 'start_date' | 'end_date', type: 'month' | 'year', value: string): void {
        const experience = this.experiences().find(exp => exp.id === expId);
        
        if (experience && value) {
            const currentDate = this.parseDate(field === 'start_date' ? experience.start_date : experience.end_date);
            
            let month = type === 'month' ? value : currentDate.month;
            let year = type === 'year' ? value : currentDate.year;
            
            if (!month) {
                month = '01';
            }
            if (!year) {
                year = new Date().getFullYear().toString();
            }
            
            this.updateDateField(expId, field, month, year);
            
            this.autoFillOppositeDate(expId, field, month, year);
        }
    }

    protected autoFillOppositeDate(expId: string, changedField: 'start_date' | 'end_date', month: string, year: string): void {
        const experience = this.experiences().find(exp => exp.id === expId);
        if (!experience) return;
        
        const oppositeField = changedField === 'start_date' ? 'end_date' : 'start_date';
        const oppositeDate = this.parseDate(changedField === 'start_date' ? experience.end_date : experience.start_date);
        
        if (!oppositeDate.month || !oppositeDate.year) {
            if (changedField === 'start_date') {
                const endYear = (parseInt(year)).toString();
                this.updateDateField(expId, 'end_date', month, endYear);
            } else {
                const startYear = (parseInt(year)).toString();
                this.updateDateField(expId, 'start_date', month, startYear);
            }
        }
    }

    protected updateDateField(expId: string, field: 'start_date' | 'end_date', month: string, year: string): void {
        if (month && year) {
            const dateValue = `${year}-${month}`;

            const experience = this.experiences().find(exp => exp.id === expId);
            if (experience && !this.isValidDate(experience, field, dateValue)) {
                return;
            }
            
            this.updateExperience(expId, field, dateValue);
        }
    }

    protected isValidDate(experience: ExperienceType, field: 'start_date' | 'end_date', newDateValue: string): boolean {
        const newDate = new Date(newDateValue + '-01');

        if (field === 'end_date') {
            if (experience.start_date) {
                const startDate = typeof experience.start_date === 'string'
                    ? new Date(experience.start_date + '-01')
                    : new Date(experience.start_date.getFullYear(), experience.start_date.getMonth(), 1);

                return newDate >= startDate;
            }
        } else if (field === 'start_date') {
            if (experience.end_date && !experience.is_current) {
                const endDate = typeof experience.end_date === 'string'
                    ? new Date(experience.end_date + '-01')
                    : new Date(experience.end_date.getFullYear(), experience.end_date.getMonth(), 1);

                return newDate <= endDate;
            }
        }

        return true;
    }

    protected isOptionDisabled(experience: ExperienceType, field: 'start_date' | 'end_date', month: string, year: string): boolean {
        if (!month || !year) return false;

        const testDateValue = `${year}-${month}`;
        return !this.isValidDate(experience, field, testDateValue);
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

    protected removeExperience(id: string): void {
        this.onRemove.emit(id);
    }

    protected async generateSummary(): Promise<void> {
        const resume = this.resumeService.currentResume();
        if (!resume) return;

        const content = await this.resumeService.generateAIContent(resume.id, 'summary');
        if (content) {
            this.onUpdate.emit({ id: resume.id, field: 'description', value: content });
        }
    }
}
