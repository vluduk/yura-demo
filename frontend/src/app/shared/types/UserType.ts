import { UserRoleEnum } from "./UserRoleEnum";

export type UserType = {
    id: string;
    name: string;
    surname: string;
    email: string;
    role: UserRoleEnum;
    phone?: string;
    avatar_url?: string;
    career_selected?: boolean;
};
