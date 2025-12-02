import { Component, ElementRef, inject, OnInit, signal, ViewChild, WritableSignal } from "@angular/core";
import { Title } from "@shared/components/title/title";
import { Button } from "@shared/components/button/button";
import { ArticleService } from "@shared/services/article.service";
import { ArticleType } from "@shared/types/ArticleType";
import { ArticleCard } from "@components/article/article-card/article-card";

@Component({
    selector: "app-article-list",
    imports: [Title, Button, ArticleCard],
    templateUrl: "./article-list.html",
    styleUrl: "./article-list.css",
})
export class ArticleList implements OnInit {
    protected readonly articles: WritableSignal<ArticleType[]> = signal<ArticleType[]>([]);
    protected readonly recommendedArticles: WritableSignal<ArticleType[]> = signal<ArticleType[]>([]);
    protected readonly isLoading: WritableSignal<boolean> = signal<boolean>(false);
    protected readonly searchQuery: WritableSignal<string> = signal<string>("");
    protected readonly selectedCategory: WritableSignal<string | null> = signal<string | null>(null);

    protected readonly categories: string[] = ["Бізнес", "Найм", "Самозайнятість", "Освіта", "Кар'єра"];

    @ViewChild("recommendedList") recommendedListRef!: ElementRef;

    private readonly articleService: ArticleService = inject(ArticleService);
    private searchTimeout: ReturnType<typeof setTimeout> | null = null;

    ngOnInit(): void {
        this.loadArticles();
        this.loadRecommendedArticles();
    }

    protected async loadArticles(): Promise<void> {
        this.isLoading.set(true);
        try {
            const articles = await this.articleService.getArticles(
                1,
                20,
                this.searchQuery() || undefined,
                this.selectedCategory() || undefined,
            );
            this.articles.set(articles);
        } finally {
            this.isLoading.set(false);
        }
    }

    protected async loadRecommendedArticles(): Promise<void> {
        try {
            const recommended = await this.articleService.getRecommendedArticles(5);
            this.recommendedArticles.set(recommended);
        } catch (error) {
            console.error("Error loading recommended articles:", error);
        }
    }

    protected onSearchInput(query: string): void {
        this.searchQuery.set(query);

        // Debounce search - wait 300ms after user stops typing
        if (this.searchTimeout) {
            clearTimeout(this.searchTimeout);
        }

        this.searchTimeout = setTimeout(() => {
            this.loadArticles();
        }, 300);
    }

    protected onSearch(): void {
        // Immediate search on button click or enter
        if (this.searchTimeout) {
            clearTimeout(this.searchTimeout);
        }
        this.loadArticles();
    }

    protected onCategorySelect(category: string | null): void {
        this.selectedCategory.set(category);
        this.loadArticles();
    }

    protected isCategoryActive(category: string): boolean {
        return this.selectedCategory() === category;
    }

    protected scrollRecommended(direction: "left" | "right"): void {
        const container = this.recommendedListRef?.nativeElement;
        if (container) {
            const scrollAmount = 280;
            container.scrollBy({
                left: direction === "left" ? -scrollAmount : scrollAmount,
                behavior: "smooth",
            });
        }
    }
}
