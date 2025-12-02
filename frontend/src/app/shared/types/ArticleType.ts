export type ArticleType = {
    id: string;
    title: string;
    content?: string;
    summary?: string;
    image?: string;
    category?: string;
    tags?: string[];
    views?: number;
    created_at?: Date;
    updated_at?: Date;
    author?: {
        id: string;
        first_name: string;
        last_name: string;
    };
};
