import { HttpClient } from "@angular/common/http";
import { inject, Injectable, signal, WritableSignal } from "@angular/core";
import { fetchEventSource } from "@microsoft/fetch-event-source";
import { environment } from "@shared/environments/environment";
import { ConversationCreateRequestType } from "@shared/types/ConversationCreateRequestType";
import { ConversationGetRequestType } from "@shared/types/ConversationGetRequestType";
import { ConversationType } from "@shared/types/ConversationType";
import { ConversationTypeEnum } from "@shared/types/ConversationTypeEnum";
import { MessageConversationRequestType } from "@shared/types/MessageConversationRequestType";
import { MessageType } from "@shared/types/MessageType";
import { firstValueFrom, Observable, Subscriber } from "rxjs";

@Injectable({
    providedIn: "root",
})
export class ConversationService {
    private httpClient: HttpClient = inject(HttpClient);

    public readonly sidebarConversations: WritableSignal<ConversationType[]> = signal<ConversationType[]>([]);

    public addToSidebar(conversation: ConversationType): void {
        this.sidebarConversations.update((list) => [conversation, ...list]);
    }

    public setSidebarConversations(conversations: ConversationType[]): void {
        this.sidebarConversations.set(conversations);
    }

    public appendToSidebar(conversations: ConversationType[]): void {
        this.sidebarConversations.update((list) => [...list, ...conversations]);
    }

    public async getConversations(
        page: number = 1,
        limit: number = 20,
        search?: string,
        type?: ConversationTypeEnum,
    ): Promise<ConversationType[]> {
        const body: ConversationGetRequestType = {
            page,
            limit,
        };

        if (search) {
            body.search = search;
        }
        if (type) {
            body.type = type;
        }

        const res = [
            { id: "1", title: "Conversation 1", type: ConversationTypeEnum.Bussiness },
            { id: "2", title: "Conversation 2", type: ConversationTypeEnum.Hiring },
            { id: "3", title: "Conversation 3", type: ConversationTypeEnum.SelfEmployment },
        ];

        return res;

        // return await firstValueFrom<ConversationType[]>(
        //     this.httpClient.get<ConversationType[]>(environment.serverURL + "/conversations/me", {
        //         params: body,
        //     }),
        // );
    }

    public async createConversation(id: string, type: ConversationTypeEnum): Promise<ConversationType> {
        const mockTitles: Record<ConversationTypeEnum, string> = {
            [ConversationTypeEnum.Bussiness]: "Нова бізнес-бесіда",
            [ConversationTypeEnum.Hiring]: "Нова бесіда про найм",
            [ConversationTypeEnum.SelfEmployment]: "Нова бесіда про самозайнятість",
            [ConversationTypeEnum.Education]: "Нова бесіда про освіту",
            [ConversationTypeEnum.CareerPath]: "Нова бесіда про кар'єру",
        };

        const mockConversation: ConversationType = {
            id,
            title: mockTitles[type] || "Нова бесіда",
            type,
        };

        await new Promise((resolve) => setTimeout(resolve, 300));

        return mockConversation;

        // Original code (uncomment when backend is ready):
        // const body: ConversationCreateRequestType = {
        //     id,
        //     type,
        //     created_at: new Date(),
        // };
        //
        // return await firstValueFrom<ConversationType>(
        //     this.httpClient.post<ConversationType>(environment.serverURL + "/conversations/me", body),
        // );
    }

    public async getMessagesByConversationId(
        conversationId: string,
        page: number = 1,
        limit: number = 4,
    ): Promise<MessageType[]> {
        // MOCK: return empty array for new conversations, or mock messages for existing ones
        const mockMessages: Record<string, MessageType[]> = {
            "1": [
                { id: "msg-1", content: "Привіт! Як розпочати бізнес?", created_at: new Date(), is_user: true },
                {
                    id: "msg-2",
                    content: "Вітаю! Для початку бізнесу вам потрібно визначити нішу та скласти бізнес-план.",
                    created_at: new Date(),
                    is_user: false,
                },
            ],
            "2": [
                { id: "msg-3", content: "Як найняти розробника?", created_at: new Date(), is_user: true },
                {
                    id: "msg-4",
                    content: "Рекомендую почати з опису вакансії та визначення необхідних навичок.",
                    created_at: new Date(),
                    is_user: false,
                },
            ],
            "3": [
                { id: "msg-5", content: "Як стати самозайнятим?", created_at: new Date(), is_user: true },
                {
                    id: "msg-6",
                    content: "Для самозайнятості потрібно зареєструватися як ФОП та обрати групу оподаткування.",
                    created_at: new Date(),
                    is_user: false,
                },
            ],
        };

        await new Promise((resolve) => setTimeout(resolve, 200));

        return mockMessages[conversationId] || [];

        // Original code (uncomment when backend is ready):
        // const body: MessageConversationRequestType = {
        //     conversation_id: conversationId,
        //     page,
        //     limit,
        // };
        //
        // return await firstValueFrom<MessageType[]>(
        //     this.httpClient.get<MessageType[]>(environment.serverURL + `/conversations/${conversationId}`, {
        //         params: body,
        //     }),
        // );
    }

    public getMessageResponse(
        conversationId: string,
        messageId: string,
        requestText: string,
        file?: File,
    ): Observable<string> {
        // MOCK: simulate streaming AI response only
        return new Observable<string>((observer) => {
            const mockResponses: string[] = [
                "Дякую за ваше запитання! ",
                "Ось що я можу вам порадити. ",
                "По-перше, важливо розуміти контекст вашої ситуації. ",
                "По-друге, рекомендую звернути увагу на наступні аспекти. ",
                "Якщо у вас є додаткові питання, ",
                "я завжди готовий допомогти!",
            ];

            let index = 0;

            const interval = setInterval(() => {
                if (index < mockResponses.length) {
                    observer.next(mockResponses[index]);
                    index++;
                } else {
                    clearInterval(interval);
                    observer.complete();
                }
            }, 300);

            return () => clearInterval(interval);
        });

        // Original code (uncomment when backend is ready):
        // return new Observable<string>((observer: Subscriber<string>) => {
        //     const formData = new FormData();
        //
        //     formData.append("messageId", messageId);
        //     formData.append("requestText", requestText);
        //     if (file) {
        //         formData.append("file", file);
        //     }
        //
        //     fetchEventSource(environment.serverURL + `/conversations/${conversationId}/messages`, {
        //         method: "POST",
        //         body: formData,
        //         headers: {},
        //         credentials: "include",
        //         onmessage(event) {
        //             observer.next(event.data);
        //         },
        //         onclose() {
        //             observer.complete();
        //         },
        //         onerror(err) {
        //             observer.error(err);
        //         },
        //     });
        // });
    }

    public regenerateMessageResponse(conversationId: string, messageId: string): Observable<string> {
        return new Observable<string>((observer: Subscriber<string>) => {
            fetchEventSource(environment.serverURL + `/conversations/${conversationId}/messages/${messageId}`, {
                method: "POST",
                headers: {},
                credentials: "include",
                onmessage(event) {
                    console.log(event.data);
                },
                onclose() {
                    observer.complete();
                },
                onerror(err) {
                    observer.error(err);
                },
            });
        });
    }

    public changeMessageRequest(
        conversationId: string,
        messageId: string,
        requestText: string,
        file?: File,
    ): Observable<string> {
        return new Observable<string>((observer: Subscriber<string>) => {
            const formData = new FormData();

            formData.append("requestText", requestText);
            if (file) {
                formData.append("file", file);
            }

            fetchEventSource(environment.serverURL + `/conversations/${conversationId}/messages/${messageId}`, {
                method: "PUT",
                body: formData,
                headers: {},
                credentials: "include",
                onmessage(event) {
                    console.log(event.data);
                },
                onclose() {
                    observer.complete();
                },
                onerror(err) {
                    observer.error(err);
                },
            });
        });
    }
}
