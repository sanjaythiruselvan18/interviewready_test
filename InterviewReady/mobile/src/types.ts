export type Profile={role:string;experience:string;language:string};
export type Feedback={scores:Record<string,number>;worked:string;improve:string;stronger:string;followup:string|null;demoNote?:string};
export type Attempt={text:string;feedback:Feedback;created:number};
export type Session={id:string;profile:Profile;jd:string;questions:{text:string;skill:string}[];answers:Attempt[][];drafts:Record<string,string>;created:number;demo:boolean};
export type Me={id:string;email:string;profile:Profile;demo:boolean;allowance:{plan:string;remaining:number;used:number;limit:number;expires:number|null}};
