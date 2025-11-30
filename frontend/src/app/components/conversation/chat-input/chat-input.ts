import { Component, output, OutputEmitterRef, signal, WritableSignal } from "@angular/core";
import { Textarea } from "@shared/components/textarea/textarea";

@Component({
    selector: "conversation-chat-input",
    imports: [Textarea],
    templateUrl: "./chat-input.html",
    styleUrl: "./chat-input.css",
})
export class ChatInput {
    protected readonly inputText: WritableSignal<string> = signal<string>("");

    public readonly onSend: OutputEmitterRef<string> = output<string>();

    protected send(): void {
        const text = this.inputText().trim();
        if (text.length > 0) {
            this.onSend.emit(text);
            this.inputText.set("");
        }
    }
}
