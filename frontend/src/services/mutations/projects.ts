import { useMutation, useQueryClient } from "@tanstack/react-query";
import {
  createProjectAPI,
  createProjectWithTasksAPI,
} from "@/services/api/projects";
import { projectsQueryKey } from "@/services/queries/projects";
import type { Project, ProjectWithTasks } from "@/types/types";

/**
 * Seed newly created projects into the cached list so every
 * "projects" consumer (the hub, future detail pages, etc.) updates
 * optimistically without a round-trip.
 */
const prependProjectToCache = (
  queryClient: ReturnType<typeof useQueryClient>,
  project: Project,
) => {
  queryClient.setQueryData<Project[]>(projectsQueryKey, (previous = []) => {
    return [project, ...previous.filter((p) => p.id !== project.id)];
  });
};

export const useCreateProjectMutation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: createProjectAPI,
    onSuccess: (project) => {
      prependProjectToCache(queryClient, project);
    },
  });
};

export const useCreateProjectWithTasksMutation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: createProjectWithTasksAPI,
    onSuccess: (project: ProjectWithTasks) => {
      // Store the base project details in the shared cache. Task lists
      // are still owned by the existing tasks query; we invalidate it
      // so the dashboard reflects the new rows.
      prependProjectToCache(queryClient, {
        id: project.id,
        name: project.name,
        description: project.description,
        createdAt: project.createdAt,
      });
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
    },
  });
};
