import { HttpClient, HttpEvent } from "@angular/common/http";
import { inject, Injectable } from "@angular/core";
import { fetchEventSource } from "@microsoft/fetch-event-source";
import { environment } from "@shared/environments/environment";
import { ConversationRequestType } from "@shared/types/ConversationRequestType";
import { ConversationType } from "@shared/types/ConversationType";
import { MessageConversationRequestType } from "@shared/types/MessageConversationRequestType";
import { MessageType } from "@shared/types/MessageType";
import { firstValueFrom, map, Observable, Subscriber, Subscription } from "rxjs";

@Injectable({
    providedIn: "root",
})
export class ConversationService {
    private httpClient: HttpClient = inject(HttpClient);

    public async getConversations(): Promise<ConversationType[]> {
        return await firstValueFrom<ConversationType[]>(
            this.httpClient.get<ConversationType[]>(environment.serverURL + "/conversations/me"),
        );
    }

    public async createConversation(
        title: string,
        subtitles: string[],
        tags: string[],
        status: string,
    ): Promise<ConversationType> {
        const body: ConversationRequestType = {
            title,
            summary_data: JSON.stringify({
                subtitles: subtitles,
                tags: tags,
                status: status,
            }),
            created_at: new Date(),
            last_active_at: new Date(),
        };

        return await firstValueFrom<ConversationType>(
            this.httpClient.post<ConversationType>(environment.serverURL + "/conversations/me", body),
        );
    }

    public async getMessagesByConversationId(
        conversationId: string,
        page: number = 1,
        limit: number = 2,
    ): Promise<MessageType[]> {
        const body: MessageConversationRequestType = {
            conversation_id: conversationId,
            page,
            limit,
        };

        return await firstValueFrom<MessageType[]>(
            this.httpClient.get<MessageType[]>(environment.serverURL + `/conversations/${conversationId}`, {
                params: body,
            }),
        );
    }

    public getMessageResponse(conversationId: string, requestText: string, file?: File): Observable<string> {
        return new Observable<string>((observer: Subscriber<string>) => {
            const formData = new FormData();

            formData.append("requestText", requestText);
            if (file) {
                formData.append("file", file);
            }

            fetchEventSource(environment.serverURL + `/conversations/${conversationId}/messages`, {
                method: "POST",
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
