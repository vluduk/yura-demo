import { Component, inject } from "@angular/core";
import { Logo } from "@shared/components/logo/logo";
import { Link } from "@shared/components/link/link";
import { Router } from "@angular/router";
import { ConversationTypeEnum } from "@shared/types/ConversationTypeEnum";

@Component({
    selector: "app-footer",
    imports: [Logo, Link],
    templateUrl: "./footer.html",
    styleUrl: "./footer.css",
})
export class Footer {
    protected readonly conversationTypes = ConversationTypeEnum;

    private readonly router: Router = inject(Router);

    protected createConversation(convType: ConversationTypeEnum): void {
        const queryParams = convType ? { convType } : {};
        const conversationId = crypto.randomUUID();

        this.router.navigate(["/conversation", conversationId], {
            queryParams,
        });
    }
}
