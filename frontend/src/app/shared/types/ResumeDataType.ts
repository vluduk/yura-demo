export type ResumeDataType = {
    id: string;
    template_id: string;
    title?: string;
    personal_info?: PersonalInfoType;
    experience?: ExperienceType[];
    education?: EducationType[];
    skills?: SkillType[];
    languages?: LanguageType[];
    is_primary: boolean;
    created_at?: Date;
    updated_at?: Date;
};

export type PersonalInfoType = {
    first_name: string;
    last_name: string;
    email?: string;
    phone?: string;
    address?: string;
    city?: string;
    country?: string;
    // photoUrl?: string;
    summary?: string;
};

export type SocialLinkType = {
    id: string;
    platform: string;
    url: string;
    display_order?: number;
};

export type ExperienceType = {
    id: string;
    job_title: string;
    employer: string;
    city?: string;
    start_date?: Date;
    end_date?: Date;
    is_current?: boolean;
    description?: string;
    display_order?: number;
};

export type EducationType = {
    id: string;
    institution: string;
    degree: string;
    field_of_study?: string;
    start_date?: Date;
    end_date?: Date;
    is_current?: boolean;
    description?: string;
    display_order?: number;
};

export type SkillType = {
    id: string;
    name: string;
    level?: "beginner" | "intermediate" | "advanced" | "expert";
    display_order?: number;
};

export type LanguageType = {
    id: string;
    language: string;
    proficiency?: "a1" | "a2" | "b1" | "b2" | "c1" | "c2" | "native";
    display_order?: number;
};

export type ExtraActivityType = {
    id: string;
    title: string;
    organization: string;
    start_date?: Date;
    end_date?: Date;
    is_current?: boolean;
    description?: string;
    display_order?: number;
};
