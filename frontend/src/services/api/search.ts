import type { EntitySearchResponse } from "@/types/types";
import { api } from "@/services/api/client";

/** Authenticated workspace search (tasks + projects for user, global tags). */
export async function getEntitySearchAPI(query: string): Promise<EntitySearchResponse> {
  const res = await api.get<EntitySearchResponse>("/api/v1/search", {
    params: { q: query },
  });
  return res.data;
}
