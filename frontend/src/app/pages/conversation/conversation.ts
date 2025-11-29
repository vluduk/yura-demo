import {
    Component,
    computed,
    effect,
    ElementRef,
    inject,
    input,
    InputSignal,
    OnInit,
    Signal,
    signal,
    viewChild,
    WritableSignal,
} from "@angular/core";
import { MessageType } from "@shared/types/MessageType";
import { ChatInput } from "@components/conversation/chat-input/chat-input";
import { ConversationService } from "@shared/services/conversation.service";

@Component({
    selector: "chat-conversation",
    imports: [ChatInput],
    templateUrl: "./conversation.html",
    styleUrl: "./conversation.css",
})
export class Conversation implements OnInit {
    protected readonly id: InputSignal<string> = input.required<string>();

    protected readonly messages: WritableSignal<MessageType[]> = signal<MessageType[]>([]);

    protected readonly printingMessage: WritableSignal<string> = signal<string>("");

    protected readonly searchInput: WritableSignal<string> = signal<string>("");

    protected readonly isLoading: WritableSignal<boolean> = signal<boolean>(false);
    protected readonly isSearchButtonDisabled: Signal<boolean> = computed(() => {
        return this.searchInput().trim().length > 0 && this.isLoading();
    });

    protected readonly messagesContainer: Signal<ElementRef> = viewChild.required<ElementRef>("scrollContainer");

    private readonly conversationService: ConversationService = inject(ConversationService);

    constructor() {
        effect(() => {
            if (this.messages().length > 0) {
                setTimeout(() => {
                    const element: HTMLElement = this.messagesContainer()?.nativeElement;
                    if (element) {
                        element.scrollTo({ top: element.scrollHeight, behavior: "smooth" });
                    }
                }, 50);
            }
        });
    }

    ngOnInit(): void {
        this.messages.set([
            {
                id: "1",
                content: "Hello",
                created_at: new Date(),
                is_user: true,
            },
            {
                id: "2",
                content: "Hi there!",
                created_at: new Date(),
                is_user: false,
            },
            {
                id: "3",
                content: "Please help me with my order.",
                created_at: new Date(),
                is_user: true,
            },
            {
                id: "4",
                content: "Sure! Can you provide your order number?",
                created_at: new Date(),
                is_user: false,
            },
        ]);
    }

    protected getResponse() {
        this.printingMessage.set("");

        this.conversationService.getMessageResponse(this.id(), "Привіт").subscribe({
            next: (chunk) => {
                this.printingMessage.set(this.printingMessage() + chunk);
            },
            complete: () => {
                console.log("Генерація завершена");
            },
            error: (err) => {
                console.error("Помилка стріму", err);
            },
        });
    }
}
