import { ConversationTypeEnum } from "./ConversationTypeEnum";

export type ConversationCreateRequestType = {
    id: string;
    type: ConversationTypeEnum;
    created_at: Date;
};
