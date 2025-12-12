import { Component, computed, inject, OnInit, Signal, signal, WritableSignal } from "@angular/core";
import { Router } from "@angular/router";
import { ChatSearchPopupService } from "@shared/services/chatSearchPopup.service";
import { ConversationType } from "@shared/types/ConversationType";
import { ConversationTypeEnum } from "@shared/types/ConversationTypeEnum";
import { Input } from "../../../shared/components/input/input";
import { Button } from "@shared/components/button/button";
import { Title } from "@shared/components/title/title";
import { Select } from "@shared/components/select/select";

@Component({
    selector: "chat-search-popup",
    imports: [Input, Button, Title, Select],
    templateUrl: "./chat-search-popup.html",
    styleUrl: "./chat-search-popup.css",
})
export class ChatSearchPopup implements OnInit {
    private readonly popupService: ChatSearchPopupService = inject(ChatSearchPopupService);
    private readonly router: Router = inject(Router);

    protected readonly searchField: WritableSignal<string> = signal<string>("");
    protected readonly type: WritableSignal<ConversationTypeEnum | "ALL"> = signal<ConversationTypeEnum | "ALL">("ALL");

    private debounceTimeout: ReturnType<typeof setTimeout> | null = null;

    protected readonly conversationTypes = [
        { value: "ALL", label: 'Всі типи' },
        { value: ConversationTypeEnum.Business, label: 'Власний бізнес' },
        { value: ConversationTypeEnum.CareerPath, label: 'Вибір напрямку' },
        { value: ConversationTypeEnum.Education, label: 'Навчання' },
        { value: ConversationTypeEnum.Hiring, label: 'Наймана праця' },
        { value: ConversationTypeEnum.SelfEmployment, label: 'Самозайнятість' },
    ];

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

            const typeValue: ConversationTypeEnum | null = this.type() === "ALL" ? null : this.type() as ConversationTypeEnum;
            this.popupService.getSearchResults(searchFieldValue, typeValue);
        }, 300);
    }

    protected openConversation(id: string): void {
        this.router.navigate(['/conversation', id]);
        this.hidePopup();
    }

    protected getConversationType(type: string): string {
        return this.conversationTypes.find((conv_type: { value: string; label: string }) => conv_type.value === type)!.label;
    }
}
