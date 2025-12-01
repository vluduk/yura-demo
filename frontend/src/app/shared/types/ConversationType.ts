import { ConversationTypeEnum } from "./ConversationTypeEnum";

export type ConversationType = {
    id: string;
    title: string;
    conv_type?: ConversationTypeEnum;
    created_at?: Date;
    last_active_at?: Date;
};
