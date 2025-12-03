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

    private readonly MOCK_CONVERSATIONS: { id: string; title: string; type: ConversationTypeEnum }[] = [
        { id: "1", title: "Business strategy planning", type: ConversationTypeEnum.Business },
        { id: "2", title: "Hiring: frontend developer", type: ConversationTypeEnum.Hiring },
        { id: "3", title: "Self-employment tips and tricks", type: ConversationTypeEnum.SelfEmployment },
        { id: "4", title: "Education: learning Angular", type: ConversationTypeEnum.Education },
        { id: "5", title: "Career path: from junior to senior", type: ConversationTypeEnum.CareerPath },
        { id: "6", title: "Business: market analysis", type: ConversationTypeEnum.Business },
        { id: "7", title: "Hiring process improvements", type: ConversationTypeEnum.Hiring },
        { id: "8", title: "Freelance contracts for self-employment", type: ConversationTypeEnum.SelfEmployment },
        { id: "9", title: "Education roadmap for web developers", type: ConversationTypeEnum.Education },
        { id: "10", title: "Career path planning session", type: ConversationTypeEnum.CareerPath },
        // ...add more mocked items if needed...
    ];

    public showChatSearchPopup(): void {
        this.isVisible.set(true);
    }

    public hideChatSearchPopup(): void {
        this.isVisible.set(false);
    }

    public getSearchResults(searchField?: string, type?: ConversationTypeEnum | null): void {
        if (searchField != this.searchField() || type != this.type()) {
            this.page.set(1);
        }

        const requestedSearch = searchField ? searchField.trim().toLowerCase() : null;
        const requestedType = type ?? null;

        const filtered = this.MOCK_CONVERSATIONS.filter((c) => {
            if (requestedType && c.type !== requestedType) {
                return false;
            }
            if (!requestedSearch) {
                return false;
            } else if (requestedSearch.length > 0) {
                return c.title.toLowerCase().includes(requestedSearch);
            }
            return true;
        });

        const response: ConversationType[] = filtered.map((c) => ({ id: c.id, title: c.title, type: c.type }));

        this.results.set(response);

        if (searchField) {
            this.searchField.set(searchField);
        }
        if (type) {
            this.type.set(type);
        }

        this.page.update((page: number) => page + 1);

        // this.conversationService
        //     .getConversations(this.page(), 20, searchField ?? undefined, type ?? undefined)
        //     .then((response: ConversationType[]) => {
        //         this.results.set(response);

        //         if (searchField) {
        //             this.searchField.set(searchField);
        //         }
        //         if (type) {
        //             this.type.set(type);
        //         }

        //         this.page.update((page: number) => page + 1);
        //     });
    }
}
