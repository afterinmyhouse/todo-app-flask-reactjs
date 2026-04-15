import { TCreateFormSchema, TEditFormSchema } from "@/schemas/task-schema";
import { Task } from "@/types/types";
import { api } from "@/services/api/client";

export const getTasksOnUserAPI = async () => {
  const response = await api.get<Task[]>("/api/v1/tasks/user");

  return response.data;
};

export const createTaskAPI = async (data: { formData: TCreateFormSchema }) => {
  const { formData } = data;
  await api.post("/api/v1/tasks", formData);
};

export const updateTaskAPI = async (data: {
  formData: TEditFormSchema;
  taskId: string;
}) => {
  const { formData, taskId } = data;
  await api.put(`/api/v1/tasks/${taskId}`, formData);
};

export const deleteTaskAPI = async (data: { taskId: string }) => {
  const { taskId } = data;
  await api.delete(`/api/v1/tasks/${taskId}`);
};
