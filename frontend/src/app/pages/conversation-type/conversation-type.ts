import { Component, inject, signal, WritableSignal } from "@angular/core";
import { Title } from "@shared/components/title/title";
import { Button } from "@shared/components/button/button";
import { ConversationTypeEnum } from "@shared/types/ConversationTypeEnum";
import { Router } from "@angular/router";

@Component({
    selector: "app-conversation-type",
    imports: [Title, Button],
    templateUrl: "./conversation-type.html",
    styleUrl: "./conversation-type.css",
})
export class ConversationType {
    protected readonly conversationTypes = ConversationTypeEnum;

    private readonly router: Router = inject(Router);

    protected createConversation(type: ConversationTypeEnum): void {
        const newId = crypto.randomUUID();

        this.router.navigate(["/conversation", newId], {
            queryParams: { type: type },
        });
    }
}
