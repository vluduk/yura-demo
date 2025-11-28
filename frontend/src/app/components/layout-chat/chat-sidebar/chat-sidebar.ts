import { Component, signal, Signal } from "@angular/core";
import { Logo } from "@shared/components/logo/logo";
import { Button } from "@shared/components/button/button";

@Component({
    selector: "chat-sidebar",
    imports: [Logo, Button],
    templateUrl: "./chat-sidebar.html",
    styleUrl: "./chat-sidebar.css",
})
export class ChatSidebar {
    public readonly conversations: Signal<any[]> = signal([
        {
            id: "1",
            title: "Conversation 1",
        },
        {
            id: "2",
            title: "Conversation 2",
        },
        {
            id: "3",
            title: "Conversation 3",
        },
    ]);
}
