import { inject, Injectable, signal, WritableSignal } from "@angular/core";
import { ConversationTypeEnum } from "@shared/types/ConversationTypeEnum";
import { ConversationService } from "./conversation.service";
import { ConversationType } from "@shared/types/ConversationType";

@Injectable({
    providedIn: "root",
})
export class ChatSearchPopupService {
    public readonly searchField: WritableSignal<string> = signal<string>("");
    public readonly type: WritableSignal<ConversationTypeEnum | null> = signal<ConversationTypeEnum | null>(null);
    public readonly isVisible: WritableSignal<boolean> = signal<boolean>(false);

    public readonly results: WritableSignal<ConversationType[]> = signal<ConversationType[]>([]);

    private readonly page: WritableSignal<number> = signal<number>(1);

    private readonly conversationService: ConversationService = inject(ConversationService);

    public showChatSearchPopup(): void {
        this.isVisible.set(true);
        this.getSearchResults();
    }

    public hideChatSearchPopup(): void {
        this.isVisible.set(false);
        this.searchField.set("");
        this.type.set(null);
    }

    public getSearchResults(searchField?: string, type?: ConversationTypeEnum | null): void {
        if (searchField != this.searchField() || type != this.type()) {
            this.page.set(1);
        }

        if (searchField) {
            this.searchField.set(searchField);
        }
        if (type) {
            this.type.set(type);
        }

        this.conversationService
            .getConversations(this.page(), 20, searchField ?? undefined, type ?? undefined)
            .then((response: ConversationType[]) => {
                this.results.set(response);
                this.page.update((page: number) => page + 1);
            });
    }
}
