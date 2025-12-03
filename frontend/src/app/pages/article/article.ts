import { Component, ElementRef, inject, OnInit, Signal, signal, viewChild, WritableSignal } from "@angular/core";
import { ActivatedRoute, RouterLink } from "@angular/router";
import { ArticleService } from "@shared/services/article.service";
import { ArticleType } from "@shared/types/ArticleType";
import { Title } from "@shared/components/title/title";
import { Button } from "@shared/components/button/button";
import { MarkdownModule } from "ngx-markdown";
import { DatePipe } from "@angular/common";
import { ArticleCard } from "@components/article/article-card/article-card";

@Component({
    selector: "app-article",
    imports: [Title, Button, MarkdownModule, DatePipe, RouterLink, ArticleCard],
    templateUrl: "./article.html",
    styleUrl: "./article.css",
})
export class Article implements OnInit {
    protected readonly article: WritableSignal<ArticleType | null> = signal<ArticleType | null>(null);
    protected readonly isLoading: WritableSignal<boolean> = signal<boolean>(false);

    protected readonly recommendedArticles: WritableSignal<ArticleType[]> = signal<ArticleType[]>([]);

    protected readonly recommendedListRef: Signal<ElementRef> = viewChild.required<ElementRef>("recommendedList");

    private readonly route = inject(ActivatedRoute);
    private readonly articleService = inject(ArticleService);

    async ngOnInit(): Promise<void> {
        const id = this.route.snapshot.paramMap.get("id");
        if (id) {
            await this.loadArticle(id);
        }

        await this.loadRecommendedArticles();
    }

    private async loadArticle(id: string): Promise<void> {
        this.isLoading.set(true);
        try {
            const article = await this.articleService.getArticleById(id);
            this.article.set(article);
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

    protected scrollRecommended(direction: "left" | "right"): void {
        const container = this.recommendedListRef()?.nativeElement as HTMLElement;
        if (container) {
            const scrollAmount = 280;
            container.scrollBy({
                left: direction === "left" ? -scrollAmount : scrollAmount,
                behavior: "smooth",
            });
        }
    }
}
