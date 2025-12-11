import { Component, computed, inject, OnInit, Signal, signal, WritableSignal } from "@angular/core";
import { Router } from "@angular/router";
import { ChatSearchPopupService } from "@shared/services/chatSearchPopup.service";
import { ConversationType } from "@shared/types/ConversationType";
import { ConversationTypeEnum } from "@shared/types/ConversationTypeEnum";
import { Input } from "../../../shared/components/input/input";

@Component({
    selector: "chat-search-popup",
    imports: [Input],
    templateUrl: "./chat-search-popup.html",
    styleUrl: "./chat-search-popup.css",
})
export class ChatSearchPopup implements OnInit {
    private readonly popupService: ChatSearchPopupService = inject(ChatSearchPopupService);
    private readonly router: Router = inject(Router);

    protected readonly searchField: WritableSignal<string> = signal<string>("");
    protected readonly type: WritableSignal<ConversationTypeEnum | null> = signal<ConversationTypeEnum | null>(null);

    private debounceTimeout: ReturnType<typeof setTimeout> | null = null;

    protected results: Signal<ConversationType[]> = signal<ConversationType[]>([]);
    protected isVisible: Signal<boolean> = signal<boolean>(false);

    ngOnInit(): void {
        this.results = this.popupService.results;
        this.isVisible = this.popupService.isVisible;
    }

    protected hidePopup(): void {
        this.popupService.hideChatSearchPopup();
    }

    protected getSearchResults(): void {
        if (this.debounceTimeout) {
            clearTimeout(this.debounceTimeout);
        }

        this.debounceTimeout = setTimeout(() => {
            const searchFieldValue: string = this.searchField().trim();

            this.popupService.getSearchResults(searchFieldValue, this.type());
        }, 300);
    }

    protected openConversation(id: string): void {
        this.router.navigate(['/conversation', id]);
        this.hidePopup();
    }
}
