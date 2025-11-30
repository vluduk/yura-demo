import { UserRoleEnum } from "./UserRoleEnum";

export type UserType = {
    id: string;
    first_name: string;
    last_name: string;
    email: string;
    role: UserRoleEnum;
    phone?: string;
    avatar_url?: string;
    career_selected?: boolean;
};
