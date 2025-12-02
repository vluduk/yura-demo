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

    // Mock data for articles
    private readonly MOCK_ARTICLES: ArticleType[] = [
        {
            id: "1",
            title: "Як розпочати власний бізнес в Україні",
            summary:
                "Покроковий гайд для початківців про реєстрацію ФОП, вибір системи оподаткування та перші кроки в підприємництві.",
            image: "https://images.unsplash.com/photo-1664575602554-2087b04935a5?w=400",
            category: "Бізнес",
            tags: ["ФОП", "реєстрація", "податки"],
            views: 1250,
            created_at: new Date("2024-01-15"),
        },
        {
            id: "2",
            title: "Топ-10 помилок при наймі працівників",
            summary:
                "Розбираємо найпоширеніші помилки роботодавців та як їх уникнути при пошуку та наймі нових співробітників.",
            image: "https://images.unsplash.com/photo-1573497019940-1c28c88b4f3e?w=400",
            category: "Найм",
            tags: ["HR", "рекрутинг", "співбесіда"],
            views: 890,
            created_at: new Date("2024-01-20"),
        },
        {
            id: "3",
            title: "Фріланс vs Офіс: що обрати?",
            summary:
                "Порівняння переваг та недоліків віддаленої роботи та офісної зайнятості для різних типів спеціалістів.",
            image: "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=400",
            category: "Самозайнятість",
            tags: ["фріланс", "віддалена робота", "кар'єра"],
            views: 2100,
            created_at: new Date("2024-02-01"),
        },
        {
            id: "4",
            title: "Безкоштовні курси програмування 2024",
            summary: "Огляд найкращих безкоштовних онлайн-курсів для вивчення програмування з нуля.",
            image: "https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=400",
            category: "Освіта",
            tags: ["програмування", "курси", "IT"],
            views: 3400,
            created_at: new Date("2024-02-10"),
        },
        {
            id: "5",
            title: "Як побудувати кар'єру в IT без досвіду",
            summary: "Реальні історії та поради від людей, які успішно перейшли в IT-сферу з інших професій.",
            image: "https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=400",
            category: "Кар'єра",
            tags: ["IT", "зміна професії", "junior"],
            views: 4500,
            created_at: new Date("2024-02-15"),
        },
        {
            id: "6",
            title: "Маркетинг для малого бізнесу",
            summary: "Ефективні маркетингові стратегії з мінімальним бюджетом для невеликих компаній.",
            image: "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=400",
            category: "Бізнес",
            tags: ["маркетинг", "SMM", "реклама"],
            views: 780,
            created_at: new Date("2024-02-20"),
        },
        {
            id: "7",
            title: "Як провести ефективну співбесіду",
            summary: "Техніки та питання для оцінки кандидатів на різні позиції.",
            image: "https://images.unsplash.com/photo-1565688534245-05d6b5be184a?w=400",
            category: "Найм",
            tags: ["співбесіда", "HR", "оцінка"],
            views: 560,
            created_at: new Date("2024-03-01"),
        },
        {
            id: "8",
            title: "Податки для самозайнятих: повний гайд",
            summary: "Все про оподаткування ФОП: групи, ставки, звітність та оптимізація.",
            image: "https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=400",
            category: "Самозайнятість",
            tags: ["податки", "ФОП", "звітність"],
            views: 1800,
            created_at: new Date("2024-03-10"),
        },
    ];

    private readonly MOCK_RECOMMENDED: ArticleType[] = [
        this.MOCK_ARTICLES[0],
        this.MOCK_ARTICLES[3],
        this.MOCK_ARTICLES[4],
        this.MOCK_ARTICLES[5],
        this.MOCK_ARTICLES[7],
    ];

    public async getArticles(
        page: number = 1,
        limit: number = 20,
        search?: string,
        category?: string,
    ): Promise<ArticleType[]> {
        this.isLoading.set(true);

        // Simulate network delay
        await new Promise((resolve) => setTimeout(resolve, 300));

        try {
            let filtered = [...this.MOCK_ARTICLES];

            // Filter by search query
            if (search && search.trim().length > 0) {
                const query = search.toLowerCase();
                filtered = filtered.filter(
                    (article) =>
                        article.title.toLowerCase().includes(query) ||
                        article.summary?.toLowerCase().includes(query) ||
                        article.tags?.some((tag) => tag.toLowerCase().includes(query)),
                );
            }

            // Filter by category
            if (category) {
                filtered = filtered.filter((article) => article.category === category);
            }

            // Pagination
            const startIndex = (page - 1) * limit;
            const paginated = filtered.slice(startIndex, startIndex + limit);

            this.articles.set(paginated);
            return paginated;
        } finally {
            this.isLoading.set(false);
        }

        // Original code (uncomment when backend is ready):
        // const params: any = {
        //     page: page.toString(),
        //     limit: limit.toString(),
        // };
        // if (search) {
        //     params.search = search;
        // }
        // if (category) {
        //     params.category = category;
        // }
        // try {
        //     const response = await firstValueFrom<ArticleType[]>(
        //         this.httpClient.get<ArticleType[]>(environment.serverURL + "/articles", { params }),
        //     );
        //     this.articles.set(response);
        //     return response;
        // } catch (error) {
        //     console.error("Error fetching articles:", error);
        //     return [];
        // } finally {
        //     this.isLoading.set(false);
        // }
    }

    public async getArticleById(id: string): Promise<ArticleType | null> {
        // Simulate network delay
        await new Promise((resolve) => setTimeout(resolve, 200));

        const article = this.MOCK_ARTICLES.find((a) => a.id === id);
        return article || null;

        // Original code (uncomment when backend is ready):
        // try {
        //     return await firstValueFrom<ArticleType>(
        //         this.httpClient.get<ArticleType>(environment.serverURL + `/articles/${id}`),
        //     );
        // } catch (error) {
        //     console.error("Error fetching article:", error);
        //     return null;
        // }
    }

    public async searchArticles(query: string): Promise<ArticleType[]> {
        return this.getArticles(1, 20, query);
    }

    public async getRecommendedArticles(limit: number = 5): Promise<ArticleType[]> {
        // Simulate network delay
        await new Promise((resolve) => setTimeout(resolve, 200));

        return this.MOCK_RECOMMENDED.slice(0, limit);

        // Original code (uncomment when backend is ready):
        // try {
        //     return await firstValueFrom<ArticleType[]>(
        //         this.httpClient.get<ArticleType[]>(environment.serverURL + "/articles/recommended", {
        //             params: { limit: limit.toString() },
        //         }),
        //     );
        // } catch (error) {
        //     console.error("Error fetching recommended articles:", error);
        //     return [];
        // }
    }
}
