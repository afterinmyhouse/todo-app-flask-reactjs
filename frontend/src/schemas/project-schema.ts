import { z } from "zod";

/**
 * Mirrors the server contract for POST /api/v1/add-project.
 *
 * Validation limits match the backend schema in
 * `backend/flaskr/schemas/plain_schema.py::PlainCreateProjectSchema`
 * so most form errors surface client-side without a round trip.
 */
export const CreateProjectSchema = z.object({
  name: z
    .string()
    .trim()
    .min(1, { message: "Name is required" })
    .max(60, { message: "Max length is 60 characters" }),
  description: z
    .string()
    .trim()
    .max(280, { message: "Max length is 280 characters" })
    .optional()
    .default(""),
});

export type TCreateProjectSchema = z.infer<typeof CreateProjectSchema>;

const TaskStatusEnum = z.enum(["PENDING", "IN_PROGRESS", "COMPLETED"]);

/**
 * One row of the "tasks" field array on the New Project With Tasks form.
 *
 * ``tagId`` is optional and carries an empty string when the user has
 * not picked a tag; the outer schema maps it to ``undefined`` before
 * hitting the wire so the backend's "must exist" check never fires
 * for omitted tags.
 */
export const ProjectTaskRowSchema = z.object({
  title: z
    .string()
    .trim()
    .min(1, { message: "Title is required" })
    .max(200, { message: "Max length is 200 characters" }),
  content: z
    .string()
    .trim()
    .max(2000, { message: "Max length is 2000 characters" })
    .optional()
    .default(""),
  status: TaskStatusEnum.default("PENDING"),
  tagId: z.string().optional().default(""),
});

export type TProjectTaskRow = z.infer<typeof ProjectTaskRowSchema>;

/** Top-level schema for POST /api/v1/add-project-with-tasks. */
export const CreateProjectWithTasksSchema = CreateProjectSchema.extend({
  tasks: z
    .array(ProjectTaskRowSchema)
    .min(1, { message: "At least one task is required" })
    .max(50, { message: "At most 50 tasks allowed" })
    .superRefine((tasks, ctx) => {
      // Duplicate-title detection mirrors the backend DUPLICATE_TASK_TITLE
      // rule so users see the error before hitting the server.
      const seen = new Map<string, number>();
      tasks.forEach((t, index) => {
        const key = t.title.trim().toLowerCase();
        if (!key) return;
        if (seen.has(key)) {
          ctx.addIssue({
            code: z.ZodIssueCode.custom,
            path: [index, "title"],
            message: "Duplicate task title in request",
          });
        } else {
          seen.set(key, index);
        }
      });
    }),
});

export type TCreateProjectWithTasksSchema = z.infer<
  typeof CreateProjectWithTasksSchema
>;
