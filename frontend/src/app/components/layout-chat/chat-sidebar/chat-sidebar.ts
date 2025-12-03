import { Component, computed, inject, Input, OnDestroy, OnInit, Signal, signal, WritableSignal } from "@angular/core";
import { Logo } from "@shared/components/logo/logo";
import { Button } from "@shared/components/button/button";
import { RouterLink, Router } from "@angular/router";
import { ConversationService } from "@shared/services/conversation.service";
import { ConversationType } from "@shared/types/ConversationType";
import { ChatSearchPopupService } from "@shared/services/chatSearchPopup.service";
import { ConversationTypeEnum } from "@shared/types/ConversationTypeEnum";

@Component({
    selector: "chat-sidebar",
    imports: [Logo, Button, RouterLink],
    templateUrl: "./chat-sidebar.html",
    styleUrl: "./chat-sidebar.css",
})
export class ChatSidebar implements OnInit, OnDestroy {
    protected readonly conversations: Signal<ConversationType[]> = computed<ConversationType[]>(() =>
        this.conversationService.sidebarConversations(),
    );

    protected readonly activeConversationId: WritableSignal<string> = signal<string>("");

    @Input()
    set conversationId(id: string) {
        this.activeConversationId.set(id || "");
    }

    protected readonly isConversationsCollapsed: WritableSignal<boolean> = signal<boolean>(false);

    protected readonly isSidebarCollapsed: WritableSignal<boolean> = signal<boolean>(false);

    private readonly isInitialLoad: WritableSignal<boolean> = signal<boolean>(true);
    private readonly converastionPage: WritableSignal<number> = signal<number>(1);

    protected readonly isSearchVisible: WritableSignal<boolean> = signal<boolean>(false);

    protected readonly conversationTypes = ConversationTypeEnum;
    protected readonly openMenuId: WritableSignal<string | null> = signal<string | null>(null);

    private readonly router: Router = inject(Router);
    private readonly conversationService: ConversationService = inject(ConversationService);
    private readonly chatSearchPopupService = inject(ChatSearchPopupService);

    constructor() {
        document.addEventListener("click", this._onDocumentClick);
        document.addEventListener("keydown", this._onDocumentKeydown);
    }

    async ngOnInit(): Promise<void> {
        await this.loadInitialConversations();
    }

    ngOnDestroy(): void {
        document.removeEventListener("click", this._onDocumentClick);
        document.removeEventListener("keydown", this._onDocumentKeydown);
    }

    private _onDocumentClick = (evt: MouseEvent) => {
        if (!this.openMenuId()) return;

        const path = (evt.composedPath && evt.composedPath()) || (evt as any).path || [];
        for (const element of path) {
            if (!element || !(element as any).classList) continue;
            const cls = (element as any).classList;
            if (
                cls.contains &&
                (cls.contains("menu__dropdown") || cls.contains("menu__toggle") || cls.contains("item__menu"))
            ) {
                return;
            }
        }

        this.hideMenu();
    };

    private _onDocumentKeydown = (evt: KeyboardEvent) => {
        if (evt.key === "Escape" || evt.key === "Esc") {
            this.hideMenu();
        }
    };

    private async loadInitialConversations(): Promise<void> {
        if (this.conversationService.sidebarConversations().length === 0) {
            await this.getConversations();
        }
    }

    protected async getConversations(): Promise<void> {
        await this.conversationService
            .getConversations(this.converastionPage())
            .then((response: ConversationType[]) => {
                if (this.isInitialLoad()) {
                    this.conversationService.setSidebarConversations(response);
                    this.isInitialLoad.set(false);
                } else {
                    this.conversationService.appendToSidebar(response);
                }
                this.converastionPage.update((page: number) => page + 1);
            });
    }

    protected showSearchPopup(): void {
        this.chatSearchPopupService.showChatSearchPopup();
    }

    protected openConversation(conversationId: string, type: ConversationTypeEnum | undefined): void {
        const queryParams = type ? { type } : {};
        this.router.navigate(["/conversation", conversationId], {
            queryParams,
        });
    }

    protected showMenu(conversationId: string): void {
        this.openMenuId.set(conversationId);
    }

    protected hideMenu(): void {
        this.openMenuId.set(null);
    }

    protected async renameConversation(conversationId: string): Promise<void> {
        const current = this.conversationService.sidebarConversations().find((c) => c && c.id === conversationId);
        const currentTitle = current?.title || "";
        const newTitle = prompt("Enter new conversation title:", currentTitle);
        if (!newTitle || newTitle.trim() === "") return;

        try {
            await this.conversationService.renameConversation(conversationId, newTitle.trim());
            this.hideMenu();
        } catch (e) {
            console.error("Rename failed", e);
            alert("Failed to rename conversation");
        }
    }

    protected async deleteConversation(conversationId: string): Promise<void> {
        const ok = confirm("Are you sure you want to delete this conversation? This action cannot be undone.");
        if (!ok) return;

        try {
            await this.conversationService.deleteConversation(conversationId);
            this.hideMenu();
        } catch (e) {
            console.error("Delete failed", e);
            alert("Failed to delete conversation");
        }
    }

    protected toggleConversationsCollapse(): void {
        this.isConversationsCollapsed.update((value: boolean) => !value);
    }

    protected toggleSidebarCollapse(): void {
        this.isSidebarCollapsed.update((value: boolean) => !value);
    }
}
