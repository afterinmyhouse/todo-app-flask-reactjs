import { useQuery } from "@tanstack/react-query";
import { getTagsAPI } from "@/services/api/tags";

export const useGetTagsQuery = () => {
  return useQuery({
    queryKey: ["tags"],
    queryFn: getTagsAPI,
  });
};
