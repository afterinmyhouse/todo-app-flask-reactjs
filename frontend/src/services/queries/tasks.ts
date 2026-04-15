import { useQuery } from "@tanstack/react-query";
import { getTasksOnUserAPI } from "@/services/api/tasks";

export const useGetTasksOnUserQuery = () => {
  return useQuery({
    queryKey: ["tasks"],
    queryFn: getTasksOnUserAPI,
  });
};
