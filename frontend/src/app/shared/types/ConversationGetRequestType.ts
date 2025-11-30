import { ConversationTypeEnum } from "./ConversationTypeEnum";

export type ConversationGetRequestType = {
    page?: number;
    limit?: number;
    search?: string;
    type?: ConversationTypeEnum;
};
