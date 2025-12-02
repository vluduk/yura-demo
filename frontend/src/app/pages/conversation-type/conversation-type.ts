import { Component, inject } from "@angular/core";
import { Title } from "@shared/components/title/title";
import { Button } from "@shared/components/button/button";
import { ConversationTypeEnum } from "@shared/types/ConversationTypeEnum";
import { Router } from "@angular/router";
import { ConversationService } from "@shared/services/conversation.service";

@Component({
    selector: "app-conversation-type",
    imports: [Title, Button],
    templateUrl: "./conversation-type.html",
    styleUrl: "./conversation-type.css",
})
export class ConversationType {
    protected readonly conversationTypes = ConversationTypeEnum;

    private readonly router: Router = inject(Router);
    private readonly conversationService: ConversationService = inject(ConversationService);

    protected async createConversation(type: ConversationTypeEnum): Promise<void> {
        try {
            // Remove any ephemeral/unsent conversations first (e.g. previously created "new chat" placeholders)
            this.conversationService.cleanupUnsavedConversations();

            const conv = await this.conversationService.createConversation('', type);
            this.conversationService.addToSidebar(conv);
            this.router.navigate(["/conversation", conv.id], {
                queryParams: { type: type },
            });
        } catch (err) {
            console.error('Failed to create conversation', err);
        }
    }
}
