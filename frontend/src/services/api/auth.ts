import { api } from "@/services/api/client";

export type CurrentUser = {
  id: string;
  username: string;
  email: string;
};

/** `GET /api/v1/auth/me` — requires `Authorization: Bearer` (axios interceptor). */
export async function fetchCurrentUser(): Promise<CurrentUser> {
  const { data } = await api.get<CurrentUser>("/api/v1/auth/me");
  return data;
}
