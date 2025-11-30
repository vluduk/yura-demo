import { Component, computed, inject, Signal, signal, WritableSignal } from "@angular/core";
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
export class ChatSearchPopup {
    private readonly popupService: ChatSearchPopupService = inject(ChatSearchPopupService);

    protected readonly searchField: WritableSignal<string> = signal<string>("");
    protected readonly type: WritableSignal<ConversationTypeEnum | null> = signal<ConversationTypeEnum | null>(null);

    private debounceTimeout: ReturnType<typeof setTimeout> | null = null;

    protected readonly results: Signal<ConversationType[]> = computed<ConversationType[]>(() =>
        this.popupService.results(),
    );
    protected readonly isVisible: Signal<boolean> = computed<boolean>(() => this.popupService.isVisible());

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
}
