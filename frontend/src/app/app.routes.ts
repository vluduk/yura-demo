import { Routes } from "@angular/router";

export const routes: Routes = [
    {
        path: "",
        loadComponent: () => import("@layouts/layout-main/layout-main").then((m) => m.LayoutMain),
        children: [
            {
                path: "",
                loadComponent: () => import("@pages/main/main").then((m) => m.Main),
            },
            {
                path: "articles",
                loadComponent: () => import("@pages/article-list/article-list").then((m) => m.ArticleList),
            },
            {
                path: "article/:id",
                loadComponent: () => import("@pages/article/article").then((m) => m.Article),
            },
        ],
    },
    {
        path: "auth",
        loadComponent: () => import("@layouts/layout-auth/layout-auth").then((m) => m.LayoutAuth),
        children: [
            {
                path: "login",
                loadComponent: () => import("@components/auth/login/login").then((m) => m.Login),
            },
            {
                path: "signup",
                loadComponent: () => import("@components/auth/signup/signup").then((m) => m.Signup),
            },
            {
                path: "",
                redirectTo: "login",
                pathMatch: "full",
            },
            {
                path: "**",
                redirectTo: "login",
                pathMatch: "full",
            },
        ],
    },
    {
        path: "conversation",
        loadComponent: () => import("@layouts/layout-chat/layout-chat").then((m) => m.LayoutChat),
        children: [
            {
                path: "",
                loadComponent: () =>
                    import("@pages/conversation-type/conversation-type").then((m) => m.ConversationType),
            },
            {
                path: "library",
                loadComponent: () => import("@pages/library/library").then((m) => m.Library),
            },
            {
                path: ":conversationId",
                loadComponent: () => import("@pages/conversation/conversation").then((m) => m.Conversation),
            },
            {
                path: "",
                redirectTo: "",
                pathMatch: "full",
            },
            {
                path: "**",
                redirectTo: "",
                pathMatch: "full",
            },
        ],
    },
    {
        path: "admin",
        loadComponent: () => import("@layouts/layout-admin/layout-admin").then((m) => m.LayoutAdmin),
        children: [
            {
                path: "articles",
                loadComponent: () => import("@pages/admin-articles/admin-articles").then((m) => m.AdminArticles),
            },
            {
                path: "article-categories",
                loadComponent: () =>
                    import("@pages/admin-article-categories/admin-article-categories").then(
                        (m) => m.AdminArticleCategories,
                    ),
            },
            {
                path: "books",
                loadComponent: () => import("@pages/admin-books/admin-books").then((m) => m.AdminBooks),
            },
            {
                path: "",
                redirectTo: "articles",
                pathMatch: "full",
            },
            {
                path: "**",
                redirectTo: "articles",
                pathMatch: "full",
            },
        ],
    },
    {
        path: "**",
        redirectTo: "",
        pathMatch: "full",
    },
];
