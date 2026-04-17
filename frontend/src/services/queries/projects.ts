import { useQuery } from "@tanstack/react-query";
import type { Project } from "@/types/types";

/**
 * React Query key used for the projects list.
 *
 * The backend currently exposes POST-only project endpoints, so we keep a
 * client-side cache under this key and seed it from the create mutations.
 * The moment a ``GET /api/v1/projects`` endpoint lands, wire its fetcher
 * into the ``queryFn`` below and every screen that uses this query will
 * pick up the network-backed data automatically.
 */
export const projectsQueryKey = ["projects"] as const;

export const useGetProjectsQuery = () => {
  return useQuery<Project[]>({
    queryKey: projectsQueryKey,
    // Cache-only: resolve immediately with whatever the mutations have
    // written. ``staleTime: Infinity`` prevents refetch loops until a
    // real fetcher replaces this placeholder.
    queryFn: async () => [],
    staleTime: Infinity,
    initialData: [],
  });
};
