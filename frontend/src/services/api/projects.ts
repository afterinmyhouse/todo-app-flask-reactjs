import { api } from "@/services/api/client";
import type {
  TCreateProjectSchema,
  TCreateProjectWithTasksSchema,
} from "@/schemas/project-schema";
import type { Project, ProjectWithTasks } from "@/types/types";

/** POST /api/v1/add-project — create a standalone project. */
export const createProjectAPI = async (
  formData: TCreateProjectSchema,
): Promise<Project> => {
  const response = await api.post<Project>("/api/v1/add-project", formData);
  return response.data;
};

/**
 * POST /api/v1/add-project-with-tasks — create a project + 1..50 tasks
 * atomically. Optional ``tagId`` values that are empty strings are
 * stripped here so the server's "must exist" check never fires for
 * omitted tags.
 */
export const createProjectWithTasksAPI = async (
  formData: TCreateProjectWithTasksSchema,
): Promise<ProjectWithTasks> => {
  const payload = {
    ...formData,
    tasks: formData.tasks.map(({ tagId, ...rest }) => ({
      ...rest,
      ...(tagId ? { tagId } : {}),
    })),
  };
  const response = await api.post<ProjectWithTasks>(
    "/api/v1/add-project-with-tasks",
    payload,
  );
  return response.data;
};
