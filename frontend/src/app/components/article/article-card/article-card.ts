import { Component, input, InputSignal, output, OutputEmitterRef } from "@angular/core";
import { ArticleType } from "@shared/types/ArticleType";
import { RouterLink } from "@angular/router";

@Component({
    selector: "app-article-card",
    imports: [RouterLink],
    templateUrl: "./article-card.html",
    styleUrl: "./article-card.css",
})
export class ArticleCard {
    public readonly article: InputSignal<ArticleType> = input.required<ArticleType>();
    public readonly variant: InputSignal<"default" | "small" | "horizontal"> = input<
        "default" | "small" | "horizontal"
    >("default");

    public readonly onClick: OutputEmitterRef<ArticleType> = output<ArticleType>();
    public readonly onTagClick: OutputEmitterRef<string> = output<string>();

    protected handleClick(): void {
        this.onClick.emit(this.article());
    }

    protected handleTagClick(event: Event, tag: string): void {
        event.stopPropagation();
        event.preventDefault();
        this.onTagClick.emit(tag);
    }

    protected formatDate(date: Date): string {
        const d = new Date(date);
        return d.toLocaleDateString("uk-UA", {
            day: "numeric",
            month: "short",
            year: "numeric",
        });
    }
}
