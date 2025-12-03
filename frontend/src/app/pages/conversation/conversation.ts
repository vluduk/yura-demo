import {
    Component,
    computed,
    effect,
    ElementRef,
    inject,
    Input,
    OnInit,
    Signal,
    signal,
    viewChild,
    WritableSignal,
} from "@angular/core";
import { MessageType } from "@shared/types/MessageType";
import { ChatInput, ChatInputMessage } from "@components/conversation/chat-input/chat-input";
import { ConversationService } from "@shared/services/conversation.service";
import { ConversationTypeEnum } from "@shared/types/ConversationTypeEnum";
import { Button } from "@shared/components/button/button";
import { MarkdownModule } from "ngx-markdown";

@Component({
    selector: "chat-conversation",
    imports: [ChatInput, Button, MarkdownModule],
    templateUrl: "./conversation.html",
    styleUrl: "./conversation.css",
})
export class Conversation {
    protected readonly currentConversationId: WritableSignal<string> = signal<string>("");
    protected readonly currentConversationType: WritableSignal<ConversationTypeEnum | null> =
        signal<ConversationTypeEnum | null>(null);

    protected readonly messages: WritableSignal<MessageType[]> = signal<MessageType[]>([]);

    protected readonly printingMessage: WritableSignal<string> = signal<string>("");

    protected readonly searchInput: WritableSignal<string> = signal<string>("");

    protected readonly isLoading: WritableSignal<boolean> = signal<boolean>(false);
    protected readonly isSearchButtonDisabled: Signal<boolean> = computed<boolean>(() => {
        return this.searchInput().trim().length > 0 && this.isLoading();
    });

    protected readonly copiedMessageId: WritableSignal<string | null> = signal<string | null>(null);
    private copyTimeout: ReturnType<typeof setTimeout> | null = null;

    protected readonly messagesContainer: Signal<ElementRef> = viewChild.required<ElementRef>("scrollContainer");

    private readonly conversationService: ConversationService = inject(ConversationService);

    @Input()
    set conversationId(id: string) {
        console.log("id input:", id);
        this.currentConversationId.set(id);

        this.getMessages();
    }

    @Input()
    set type(type: ConversationTypeEnum | null) {
        console.log("type input:", type);
        this.currentConversationType.set(type as ConversationTypeEnum);
    }

    constructor() {
        effect(() => {
            if (this.messages().length > 0) {
                this.scrollToBottom();
            }
        });

        effect(() => {
            if (this.printingMessage().length > 0) {
                this.scrollToBottom();
            }
        });
    }

    private scrollToBottom(): void {
        setTimeout(() => {
            const element: HTMLElement = this.messagesContainer()?.nativeElement;
            if (element) {
                element.scrollTo({ top: element.scrollHeight, behavior: "smooth" });
            }
        }, 50);
    }

    protected getMessages(): void {
        this.conversationService
            .getMessagesByConversationId(this.currentConversationId())
            .then((response: MessageType[]) => {
                this.messages.set(response);
            });
    }

    protected async getResponse(message?: ChatInputMessage): Promise<void> {
        if (!message || (!message.text && !message.file)) {
            return;
        }

        const messageId = crypto.randomUUID();

        let displayContent = message.text;
        if (message.file) {
            displayContent = message.text ? `${message.text}\n\n${message.file.name}` : `${message.file.name}`;
        }

        const userMessage: MessageType = {
            id: messageId,
            content: displayContent,
            created_at: new Date(),
            is_user: true,
        };
        this.messages.update((msgs) => [...msgs, userMessage]);

        this.printingMessage.set("");
        this.isLoading.set(true);

        this.conversationService
            .getMessageResponse(
                this.currentConversationId(),
                messageId,
                message.text,
                this.currentConversationType() || undefined,
                message.file,
            )
            .subscribe({
                next: (chunk) => {
                    this.printingMessage.update((value: string) => value + chunk);
                },
                complete: () => {
                    console.log("Генерація завершена");

                    if (this.printingMessage().length > 0) {
                        const aiMessage: MessageType = {
                            id: crypto.randomUUID(),
                            content: this.printingMessage(),
                            created_at: new Date(),
                            is_user: false,
                        };
                        this.messages.update((msgs) => [...msgs, aiMessage]);
                        this.printingMessage.set("");
                    }

                    this.isLoading.set(false);
                },
                error: (err) => {
                    console.error("Помилка стріму", err);
                    this.isLoading.set(false);
                },
            });
    }

    protected async copyMessage(message: MessageType): Promise<void> {
        try {
            await navigator.clipboard.writeText(message.content);
            this.copiedMessageId.set(message.id);

            if (this.copyTimeout) {
                clearTimeout(this.copyTimeout);
            }

            this.copyTimeout = setTimeout(() => {
                this.copiedMessageId.set(null);
                this.copyTimeout = null;
            }, 2000);
        } catch (err) {
            console.error("Failed to copy text:", err);
        }
    }

    protected isCopied(messageId: string): boolean {
        return this.copiedMessageId() === messageId;
    }

    protected readonly editingMessageId: WritableSignal<string | null> = signal<string | null>(null);
    protected readonly editingText: WritableSignal<string> = signal<string>("");

    protected startEditing(message: MessageType): void {
        this.editingMessageId.set(message.id);
        this.editingText.set(message.content);
    }

    protected cancelEditing(): void {
        this.editingMessageId.set(null);
        this.editingText.set("");
    }

    protected async confirmEditing(): Promise<void> {
        const editingId = this.editingMessageId();
        const newText = this.editingText().trim();

        if (!editingId || !newText) {
            this.cancelEditing();
            return;
        }

        // Find the index of the message being edited
        const messages = this.messages();
        const messageIndex = messages.findIndex((m) => m.id === editingId);

        if (messageIndex === -1) {
            this.cancelEditing();
            return;
        }

        // Remove all messages after the edited one (including AI responses)
        const messagesBeforeEdit = messages.slice(0, messageIndex);

        // Update the edited message
        const editedMessage: MessageType = {
            ...messages[messageIndex],
            content: newText,
        };

        // Set messages to only include messages before edit + edited message
        this.messages.set([...messagesBeforeEdit, editedMessage]);

        // Clear editing state
        this.cancelEditing();

        // Get new AI response for the edited message
        this.printingMessage.set("");
        this.isLoading.set(true);

        this.conversationService
            .getMessageResponse(
                this.currentConversationId(),
                editedMessage.id,
                newText,
                this.currentConversationType() || undefined,
            )
            .subscribe({
                next: (chunk) => {
                    this.printingMessage.update((value: string) => value + chunk);
                },
                complete: () => {
                    console.log("Генерація завершена");

                    if (this.printingMessage().length > 0) {
                        const aiMessage: MessageType = {
                            id: crypto.randomUUID(),
                            content: this.printingMessage(),
                            created_at: new Date(),
                            is_user: false,
                        };
                        this.messages.update((msgs) => [...msgs, aiMessage]);
                        this.printingMessage.set("");
                    }

                    this.isLoading.set(false);
                },
                error: (err) => {
                    console.error("Помилка стріму", err);
                    this.isLoading.set(false);
                },
            });
    }

    protected isEditing(messageId: string): boolean {
        return this.editingMessageId() === messageId;
    }

    protected isLastAiMessage(messageId: string): boolean {
        for (let i = this.messages().length - 1; i >= 0; i--) {
            if (!this.messages()[i].is_user) {
                return this.messages()[i].id === messageId;
            }
        }
        return false;
    }

    protected async regenerateLastResponse(): Promise<void> {
        let lastAiIndex = -1;
        for (let i = this.messages().length - 1; i >= 0; i--) {
            if (!this.messages()[i].is_user) {
                lastAiIndex = i;
                break;
            }
        }

        if (lastAiIndex === -1) {
            return;
        }

        let lastUserMessage: MessageType | null = null;
        for (let i = lastAiIndex - 1; i >= 0; i--) {
            if (this.messages()[i].is_user) {
                lastUserMessage = this.messages()[i];
                break;
            }
        }

        if (!lastUserMessage) {
            return;
        }

        const messagesWithoutLastAi = this.messages().slice(0, lastAiIndex);
        this.messages.set(messagesWithoutLastAi);

        this.printingMessage.set("");
        this.isLoading.set(true);

        this.conversationService
            .getMessageResponse(
                this.currentConversationId(),
                lastUserMessage.id,
                lastUserMessage.content,
                this.currentConversationType() || undefined,
            )
            .subscribe({
                next: (chunk) => {
                    this.printingMessage.update((value: string) => value + chunk);
                },
                complete: () => {
                    console.log("Перегенерація завершена");

                    if (this.printingMessage().length > 0) {
                        const aiMessage: MessageType = {
                            id: crypto.randomUUID(),
                            content: this.printingMessage(),
                            created_at: new Date(),
                            is_user: false,
                        };
                        this.messages.update((m) => [...m, aiMessage]);
                        this.printingMessage.set("");
                    }

                    this.isLoading.set(false);
                },
                error: (err) => {
                    console.error("Помилка перегенерації", err);
                    this.isLoading.set(false);
                },
            });
    }
}
