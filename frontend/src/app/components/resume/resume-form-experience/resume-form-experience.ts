import { Component, inject, input, InputSignal, output, OutputEmitterRef } from "@angular/core";
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

    // Українські назви місяців
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

    // Метод для генерації років (останні 50 років)
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
        console.log(value)
    }

    // Метод для обробки змін місяця та року з валідацією
    protected updateDateField(expId: string, field: 'start_date' | 'end_date', month: string, year: string): void {
        console.log("DGDGGD")
        if (month && year) {
            const dateValue = `${year}-${month}`;
            
            // Перевірка валідності дат
            const experience = this.experiences().find(exp => exp.id === expId);
            if (experience && !this.isValidDate(experience, field, dateValue)) {
                return; // Не оновлюємо, якщо дата невалідна
            }
            console.log(dateValue)

            
            this.updateExperience(expId, field, dateValue);
        }
    }

    // Метод для перевірки валідності дат
    protected isValidDate(experience: ExperienceType, field: 'start_date' | 'end_date', newDateValue: string): boolean {
        const newDate = new Date(newDateValue + '-01'); // Додаємо день для порівняння
        
        if (field === 'end_date') {
            // Кінцева дата не може бути раніше початкової
            if (experience.start_date) {
                const startDate = typeof experience.start_date === 'string' 
                    ? new Date(experience.start_date + '-01')
                    : new Date(experience.start_date.getFullYear(), experience.start_date.getMonth(), 1);
                    
                return newDate >= startDate;
            }
        } else if (field === 'start_date') {
            // Початкова дата не може бути пізніше кінцевої
            if (experience.end_date && !experience.is_current) {
                const endDate = typeof experience.end_date === 'string'
                    ? new Date(experience.end_date + '-01')
                    : new Date(experience.end_date.getFullYear(), experience.end_date.getMonth(), 1);
                    
                return newDate <= endDate;
            }
        }
        
        return true;
    }

    // Метод для перевірки чи місяць/рік доступні для вибору
    protected isOptionDisabled(experience: ExperienceType, field: 'start_date' | 'end_date', month: string, year: string): boolean {
        if (!month || !year) return false;
        
        const testDateValue = `${year}-${month}`;
        return !this.isValidDate(experience, field, testDateValue);
    }

    // Методи-обгортки для обробки змін місяця з валідацією
    protected onMonthChange(event: string, expId: string, field: 'start_date' | 'end_date', currentYear: string): void {
        console.log(event)
        
        if (event && currentYear) {
            const experience = this.experiences().find(exp => exp.id === expId);
            if (experience && this.isValidDate(experience, field, `${currentYear}-${event}`)) {
                this.updateDateField(expId, field, event, currentYear);
            } else {
                // Скидаємо вибір на попереднє значення
                event = this.parseDate(field === 'start_date' ? experience?.start_date : experience?.end_date).month;
            }
        }
    }

    // Методи-обгортки для обробки змін року з валідацією
    protected onYearChange(event: Event, expId: string, field: 'start_date' | 'end_date', currentMonth: string): void {
        const target = event.target as HTMLSelectElement;
        const year = target.value;
        
        if (year && currentMonth) {
            const experience = this.experiences().find(exp => exp.id === expId);
            if (experience && this.isValidDate(experience, field, `${year}-${currentMonth}`)) {
                this.updateDateField(expId, field, currentMonth, year);
            } else {
                // Скидаємо вибір на попереднє значення
                target.value = this.parseDate(field === 'start_date' ? experience?.start_date : experience?.end_date).year;
            }
        }
    }

    // Метод для парсингу дати (приймає string або Date)
    protected parseDate(dateValue: string | Date | undefined): { month: string, year: string } {
        if (!dateValue) return { month: '', year: '' };
        
        let dateString: string;
        if (dateValue instanceof Date) {
            // Конвертуємо Date в YYYY-MM формат
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
