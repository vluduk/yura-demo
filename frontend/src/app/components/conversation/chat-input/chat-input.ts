import { Component } from "@angular/core";
import { Textarea } from "@shared/components/textarea/textarea";

@Component({
    selector: "conversation-chat-input",
    imports: [Textarea],
    templateUrl: "./chat-input.html",
    styleUrl: "./chat-input.css",
})
export class ChatInput {}
