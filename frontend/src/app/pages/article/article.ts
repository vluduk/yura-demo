import { Component, inject, OnInit, signal, WritableSignal } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { ArticleService } from '@shared/services/article.service';
import { ArticleType } from '@shared/types/ArticleType';
import { Title } from '@shared/components/title/title';
import { Button } from '@shared/components/button/button';
import { MarkdownModule } from 'ngx-markdown';
import { DatePipe } from '@angular/common';

@Component({
  selector: 'app-article',
  imports: [Title, Button, MarkdownModule, DatePipe, RouterLink],
  templateUrl: './article.html',
  styleUrl: './article.css',
})
export class Article implements OnInit {
    private readonly route = inject(ActivatedRoute);
    private readonly articleService = inject(ArticleService);

    protected readonly article: WritableSignal<ArticleType | null> = signal<ArticleType | null>(null);
    protected readonly isLoading: WritableSignal<boolean> = signal<boolean>(false);

    ngOnInit(): void {
        const id = this.route.snapshot.paramMap.get('id');
        if (id) {
            this.loadArticle(id);
        }
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
}
