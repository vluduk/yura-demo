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

    constructor() {
        // When the user closes the tab/window, remove ephemeral (unsaved/new) conversations from the sidebar
        // We cannot reliably delete server-side records without a dedicated API, so remove them client-side
        if (typeof window !== "undefined") {
            window.addEventListener("beforeunload", () => {
                try {
                    this.tryDeleteEphemeralOnServer();
                } catch (e) {
                    // ignore
                }

                try {
                    this.cleanupUnsavedConversations();
                } catch (e) {
                    // ignore
                }
            });
        }
    }

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
        // Determine a sensible default title based on convType (server also has a fallback)
        const typeLabelMap: Record<ConversationTypeEnum, string> = {
            [ConversationTypeEnum.Bussiness]: "Бізнес",
            [ConversationTypeEnum.SelfEmployment]: "Самозайнятість",
            [ConversationTypeEnum.Hiring]: "Найм",
            [ConversationTypeEnum.CareerPath]: "Кар'єра",
            [ConversationTypeEnum.Education]: "Освіта",
        };

        const defaultTitle = convType ? `${typeLabelMap[convType] || convType} - новий чат` : "Нова розмова";

        const body: any = {
            title: title || defaultTitle,
        };

        if (convType) {
            // Map frontend enum values to backend ConversationType choices
            const convTypeMap: Record<ConversationTypeEnum, string> = {
                [ConversationTypeEnum.Bussiness]: "BUSINESS",
                [ConversationTypeEnum.SelfEmployment]: "SELF_EMPLOYMENT",
                [ConversationTypeEnum.Hiring]: "HIRING",
                [ConversationTypeEnum.CareerPath]: "CAREER_PATH",
                [ConversationTypeEnum.Education]: "EDUCATION",
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

    /**
     * Remove ephemeral conversations from the sidebar (client-side only).
     * Criteria: empty title OR titles that end with " - новий чат" and have no last_active_at timestamp.
     */
    public cleanupUnsavedConversations(): void {
        const kept = this.sidebarConversations().filter((conv) => {
            if (!conv) return true;
            const title = conv.title || "";
            const isDefaultNew = / - новий чат$/.test(title);
            // Keep conversation if it has last_active_at (meaning activity happened)
            if ((conv as any).last_active_at) return true;
            // Remove if empty title or default-new title
            if (title.trim() === "" || isDefaultNew) return false;
            return true;
        });

        this.sidebarConversations.set(kept);
    }

    /**
     * Try to delete ephemeral conversations on the server where possible.
     * Uses the Fetch API with `keepalive` so the browser can attempt the request during unload.
     */
    public tryDeleteEphemeralOnServer(): void {
        const toDelete = this.sidebarConversations().filter((conv) => {
            if (!conv) return false;
            const title = conv.title || "";
            const isDefaultNew = / - новий чат$/.test(title);
            if ((conv as any).last_active_at) return false;
            if (title.trim() === "" || isDefaultNew) return true;
            return false;
        });

        toDelete.forEach((conv) => {
            try {
                const url = `${environment.serverURL}/conversations/${conv.id}`;
                // Use fetch with keepalive so browser attempts it during unload
                if (typeof fetch === "function") {
                    try {
                        fetch(url, { method: "DELETE", credentials: "include", keepalive: true }).catch(() => {
                            // ignore errors
                        });
                    } catch (e) {
                        // ignore
                    }
                }
            } catch (e) {
                // ignore
            }
        });
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
            const startStream = async () => {
                let fileId: string | null = null;

                if (file) {
                    try {
                        fileId = await this.uploadFile(file);
                    } catch (error) {
                        console.error("File upload failed:", error);
                        observer.error(error);
                        return;
                    }
                }

                const body: any = {
                    content: requestText,
                };

                if (fileId) {
                    body.file_id = fileId;
                }

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
                    await fetchEventSource(url, {
                        method: "POST",
                        body: JSON.stringify(body),
                        headers: { "Content-Type": "application/json" },
                        credentials: "include",
                        onmessage(event) {
                            // If the server sends a JSON object (e.g. the final message object), we might parse it
                            // But for now, we assume the server sends chunks of text in `data`.
                            // If the server sends a special event for "done", handle it.
                            if (event.event === "end") {
                                observer.complete();
                                return;
                            }
                            // Accumulate text
                            // Note: The backend might send JSON or plain text.
                            // If it sends JSON with { content: "..." }, parse it.
                            try {
                                const data = JSON.parse(event.data);
                                if (data.content) {
                                    observer.next(data.content);
                                }
                            } catch (e) {
                                // If not JSON, just send raw data
                                observer.next(event.data);
                            }
                        },
                        onclose() {
                            observer.complete();
                        },
                        onerror(err) {
                            observer.error(err);
                            // rethrow to stop retries if needed
                            throw err;
                        },
                    });
                } catch (err) {
                    observer.error(err);
                }
            };

            startStream();
        });
    }

    private async uploadFile(file: File): Promise<string> {
        const formData = new FormData();
        formData.append("file", file);

        const response = await firstValueFrom(
            this.httpClient.post<any>(environment.serverURL + "/files/upload/", formData, {
                withCredentials: true,
            }),
        );
        return response.id;
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
