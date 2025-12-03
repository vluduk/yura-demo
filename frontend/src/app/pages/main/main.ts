import { Component, inject, OnInit, signal, WritableSignal } from "@angular/core";
import { Title } from "@shared/components/title/title";
import { Button } from "@shared/components/button/button";
import { RouterLink } from "@angular/router";
import { ArticleCard } from "@components/article/article-card/article-card";
import { ArticleList } from "@pages/article-list/article-list";
import { ArticleService } from "@shared/services/article.service";
import { ArticleType } from "@shared/types/ArticleType";

@Component({
    selector: "app-main",
    imports: [Title, Button, RouterLink],
    templateUrl: "./main.html",
    styleUrl: "./main.css",
})
export class Main implements OnInit {
    protected readonly recommendedArticles: WritableSignal<ArticleType[]> = signal<ArticleType[]>([]);

    private readonly articleService: ArticleService = inject(ArticleService);

    ngOnInit(): void {
        this.getRecommendedArticles();
    }

    protected async getRecommendedArticles(): Promise<void> {
        const recommended = await this.articleService.getRecommendedArticles(3);

        if (recommended) {
            this.recommendedArticles.set(recommended);
        }

        console.log("Recommended articles:", recommended);
    }
}
