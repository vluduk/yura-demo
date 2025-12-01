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
        // Get conversations from backend
        return await firstValueFrom<ConversationType[]>(
            this.httpClient.get<ConversationType[]>(environment.serverURL + "/conversations", {
                params: { page: page.toString(), limit: limit.toString() },
            }),
        );
    }

    public async createConversation(title?: string, convType?: ConversationTypeEnum): Promise<ConversationType> {
        const body: any = {
            title: title || "",
        };

        if (convType) {
            // Map frontend enum values to backend ConversationType choices
            const convTypeMap: Record<ConversationTypeEnum, string> = {
                [ConversationTypeEnum.Bussiness]: "Business",
                [ConversationTypeEnum.SelfEmployment]: "SelfEmployment",
                [ConversationTypeEnum.Hiring]: "Hiring",
                [ConversationTypeEnum.CareerPath]: "CareerPath",
                [ConversationTypeEnum.Education]: "Education",
            };

            body.conv_type = convTypeMap[convType] || convType;
        }

        return await firstValueFrom<ConversationType>(
            this.httpClient.post<ConversationType>(environment.serverURL + "/conversations", body),
        );
    }

    public async getMessagesByConversationId(conversationId: string): Promise<MessageType[]> {
        try {
            // Get conversation to fetch its messages
            const conversation = await firstValueFrom<any>(
                this.httpClient.get<any>(environment.serverURL + `/conversations/${conversationId}`),
            );

            // Return messages from conversation (they're included in the conversation object)
            return conversation.messages || [];
        } catch (error) {
            console.error("Error fetching messages:", error);
            return [];
        }
    }

    public getMessageResponse(
        conversationId: string,
        messageId: string,
        requestText: string,
        convType?: ConversationTypeEnum,
        file?: File,
    ): Observable<string> {
        // Call backend chat endpoint and consume SSE for character-by-character streaming
        return new Observable<string>((observer) => {
            const body: any = {
                content: requestText,
            };

            // Add conversation_id if it exists (not a new conversation)
            if (conversationId) {
                body.conversation_id = conversationId;
            }

            // Add conv_type for new conversations
            if (convType && !conversationId) {
                body.conv_type = convType;
            }

            // Use fetchEventSource to attach to an SSE stream. Backend supports `?stream=1`.
            const url = environment.serverURL + "/conversations/chat?stream=1";

            try {
                fetchEventSource(url, {
                    method: "POST",
                    body: JSON.stringify(body),
                    headers: { "Content-Type": "application/json" },
                    credentials: "include",
                    onmessage(event) {
                        try {
                            // Expecting JSON payload like {"chunk": "c"}
                            const data = JSON.parse(event.data || "{}");
                            if (data.chunk) {
                                observer.next(data.chunk);
                            } else {
                                // If message doesn't have chunk, send raw data
                                observer.next(event.data);
                            }
                        } catch (e) {
                            // fallback: forward raw event data
                            observer.next(event.data);
                        }
                    },
                    onclose() {
                        observer.complete();
                    },
                    onerror(err) {
                        observer.error(err);
                    },
                });
            } catch (err) {
                observer.error(err as any);
            }
        });
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
