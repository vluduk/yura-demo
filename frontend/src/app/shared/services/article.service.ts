import { HttpClient } from "@angular/common/http";
import { inject, Injectable, signal, WritableSignal } from "@angular/core";
import { environment } from "@shared/environments/environment";
import { ArticleType } from "@shared/types/ArticleType";
import { firstValueFrom } from "rxjs";

export type ArticleGetRequestType = {
    page?: number;
    limit?: number;
    search?: string;
    category?: string;
};

@Injectable({
    providedIn: "root",
})
export class ArticleService {
    private readonly httpClient: HttpClient = inject(HttpClient);

    public readonly articles: WritableSignal<ArticleType[]> = signal<ArticleType[]>([]);
    public readonly isLoading: WritableSignal<boolean> = signal<boolean>(false);

    public async getArticles(
        page: number = 1,
        limit: number = 20,
        search?: string,
        category?: string,
        tags?: string[],
    ): Promise<ArticleType[]> {
        this.isLoading.set(true);
        const params: any = {
            page: page.toString(),
            limit: limit.toString(),
        };
        if (search) {
            params.search = search;
        }
        if (category) {
            params.category = category;
        }
        if (tags && tags.length > 0) {
            params.tags = tags.join(",");
        }
        try {
            const response = await firstValueFrom<any>(
                this.httpClient.get<any>(environment.serverURL + "/articles/", { params }),
            );
            
            // Handle DRF pagination (results array) or direct array
            const results = Array.isArray(response) ? response : (response.results || []);

            const mapped: ArticleType[] = results.map((item: any) => ({
                id: item.id,
                title: item.title,
                summary: item.summary,
                content: item.content,
                image: item.cover_image_url,
                category: item.category?.name,
                tags: item.tags,
                views: item.views_count,
                created_at: new Date(item.created_at),
            }));

            this.articles.set(mapped);
            return mapped;
        } catch (error) {
            console.error("Error fetching articles:", error);
            return [];
        } finally {
            this.isLoading.set(false);
        }
    }

    public async getArticleById(id: string): Promise<ArticleType | null> {
        try {
            const item = await firstValueFrom<any>(
                this.httpClient.get<any>(environment.serverURL + `/articles/${id}/`),
            );
            
            return {
                id: item.id,
                title: item.title,
                summary: item.summary,
                content: item.content,
                image: item.cover_image_url,
                category: item.category?.name,
                tags: item.tags,
                views: item.views_count,
                created_at: new Date(item.created_at),
            };
        } catch (error) {
            console.error("Error fetching article:", error);
            return null;
        }
    }

    public async searchArticles(query: string): Promise<ArticleType[]> {
        return this.getArticles(1, 20, query);
    }

    public async getRecommendedArticles(limit: number = 5): Promise<ArticleType[]> {
        try {
            const response = await firstValueFrom<any>(
                this.httpClient.get<any>(environment.serverURL + "/articles/promoted/", {
                    params: { limit: limit.toString() },
                }),
            );
            
            const results = Array.isArray(response) ? response : (response.results || []);

            return results.slice(0, limit).map((item: any) => ({
                id: item.id,
                title: item.title,
                summary: item.summary,
                content: item.content,
                image: item.cover_image_url,
                category: item.category?.name,
                views: item.views_count,
                created_at: new Date(item.created_at),
            }));
        } catch (error) {
            console.error("Error fetching recommended articles:", error);
            return [];
        }
    }
}
