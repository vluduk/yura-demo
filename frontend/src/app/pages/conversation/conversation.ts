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
import { ChatInput } from "@components/conversation/chat-input/chat-input";
import { ConversationService } from "@shared/services/conversation.service";
import { ConversationTypeEnum } from "@shared/types/ConversationTypeEnum";
import { Button } from "@shared/components/button/button";

@Component({
    selector: "chat-conversation",
    imports: [ChatInput, Button],
    templateUrl: "./conversation.html",
    styleUrl: "./conversation.css",
})
export class Conversation implements OnInit {
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

    ngOnInit(): void {
        console.log(this.currentConversationType());

        // this.messages.set([
        //     {
        //         id: "1",
        //         content: "Hello",
        //         created_at: new Date(),
        //         is_user: true,
        //     },
        //     {
        //         id: "2",
        //         content: "Hi there!",
        //         created_at: new Date(),
        //         is_user: false,
        //     },
        //     {
        //         id: "3",
        //         content: "Please help me with my order.",
        //         created_at: new Date(),
        //         is_user: true,
        //     },
        //     {
        //         id: "4",
        //         content: "Sure! Can you provide your order number?",
        //         created_at: new Date(),
        //         is_user: false,
        //     },
        // ]);
    }

    protected getMessages(): void {
        this.conversationService
            .getMessagesByConversationId(this.currentConversationId())
            .then((response: MessageType[]) => {
                this.messages.set(response);
            });
    }

    protected async getResponse(requestText?: string): Promise<void> {
        if (!requestText) {
            return;
        }

        const messageId = crypto.randomUUID();

        const userMessage: MessageType = {
            id: messageId,
            content: requestText,
            created_at: new Date(),
            is_user: true,
        };
        this.messages.update((msgs) => [...msgs, userMessage]);

        this.printingMessage.set("");
        this.isLoading.set(true);

        if (this.messages().length === 1) {
            await this.conversationService
                .createConversation(
                    this.currentConversationId(),
                    this.currentConversationType() as ConversationTypeEnum,
                )
                .then((conversation) => {
                    console.log("Conversation created:", conversation);
                    this.conversationService.addToSidebar(conversation);
                });
        }

        this.conversationService.getMessageResponse(this.currentConversationId(), messageId, requestText).subscribe({
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
}
