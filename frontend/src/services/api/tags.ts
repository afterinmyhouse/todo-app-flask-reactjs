import { Tag } from "@/types/types";
import { api } from "@/services/api/client";

export const getTagsAPI = async () => {
  const response = await api.get<Tag[]>("/api/v1/tags");

  return response.data;
};
