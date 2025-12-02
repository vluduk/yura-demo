import { Component, computed, inject, OnInit, Signal, signal, WritableSignal } from "@angular/core";
import { Logo } from "@shared/components/logo/logo";
import { Button } from "@shared/components/button/button";
import { RouterLink, Router, NavigationEnd } from "@angular/router";
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
export class ChatSidebar implements OnInit {
    protected readonly conversations: Signal<ConversationType[]> = computed<ConversationType[]>(() =>
        this.conversationService.sidebarConversations(),
    );
    protected readonly activeConversationId: WritableSignal<string> = signal<string>("");

    private readonly isInitialLoad: WritableSignal<boolean> = signal<boolean>(true);
    private readonly converastionPage: WritableSignal<number> = signal<number>(1);

    protected readonly isSearchVisible: WritableSignal<boolean> = signal<boolean>(false);

    protected readonly conversationTypes = ConversationTypeEnum;
    protected readonly openMenuId: WritableSignal<string | null> = signal<string | null>(null);

    private readonly router: Router = inject(Router);
    private readonly conversationService: ConversationService = inject(ConversationService);
    private readonly chatSearchPopupService = inject(ChatSearchPopupService);

    constructor() {
        this.updateActiveIdFromUrl();

        this.router.events.subscribe((event) => {
            if (event instanceof NavigationEnd) {
                this.updateActiveIdFromUrl();
            }
        });

        // Load conversations only once on init
        this.loadInitialConversations();
    }

    private loadInitialConversations(): void {
        if (this.conversationService.sidebarConversations().length === 0) {
            this.getConversations();
        }
    }

    ngOnInit(): void {
        // Removed duplicate getConversations() call - already handled in constructor
    }

    protected getConversations(): void {
        this.conversationService.getConversations(this.converastionPage()).then((response: ConversationType[]) => {
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

    private updateActiveIdFromUrl(): void {
        const url = this.router.url || "";
        const match = url.match(/\/conversation\/([^\/\?\#]+)/);
        const urlId = match ? match[1] : "";
        const stateId = (history && (history.state as any)?.conversationId) || "";
        const resolved = urlId || stateId || "";
        this.activeConversationId.set(resolved);
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
            console.error('Rename failed', e);
            alert('Failed to rename conversation');
        }
    }

    protected async deleteConversation(conversationId: string): Promise<void> {
        const ok = confirm('Are you sure you want to delete this conversation? This action cannot be undone.');
        if (!ok) return;

        try {
            await this.conversationService.deleteConversation(conversationId);
            this.hideMenu();
        } catch (e) {
            console.error('Delete failed', e);
            alert('Failed to delete conversation');
        }
    }
}
