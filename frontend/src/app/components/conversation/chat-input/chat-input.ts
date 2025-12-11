import { Component, input, InputSignal, output, OutputEmitterRef, signal, WritableSignal } from "@angular/core";
import { Textarea } from "@shared/components/textarea/textarea";
import { Button } from "@shared/components/button/button";

export type ChatInputMessage = {
    text: string;
    file?: File;
};

@Component({
    selector: "conversation-chat-input",
    imports: [Textarea, Button],
    templateUrl: "./chat-input.html",
    styleUrl: "./chat-input.css",
})
export class ChatInput {
    protected readonly inputText: WritableSignal<string> = signal<string>("");
    protected readonly selectedFile: WritableSignal<File | null> = signal<File | null>(null);

    public readonly isLoading: InputSignal<boolean> = input<boolean>(false);

    public readonly onSend: OutputEmitterRef<ChatInputMessage> = output<ChatInputMessage>();

    protected send(): void {
        if (this.isLoading()) return;

        const text = this.inputText().trim();
        if (text.length > 0 || this.selectedFile()) {
            this.onSend.emit({
                text,
                file: this.selectedFile() || undefined,
            });
            this.inputText.set("");
            this.selectedFile.set(null);
        }
    }

    protected onFileSelect(event: Event): void {
        const input = event.target as HTMLInputElement;
        if (input.files && input.files.length > 0) {
            this.selectedFile.set(input.files[0]);
        }
    }

    protected removeFile(): void {
        this.selectedFile.set(null);
    }

    protected triggerFileInput(): void {
        const fileInput = document.getElementById("chat-file-input") as HTMLInputElement;
        fileInput?.click();
    }

    protected formatFileSize(bytes: number): string {
        if (bytes < 1024) return bytes + " B";
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
        return (bytes / (1024 * 1024)).toFixed(1) + " MB";
    }
}
