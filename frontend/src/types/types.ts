export type Tag = {
  id: string;
  name: string;
};

/** Backend task status (API / Mongo, see PlainTaskSchema). */
export type ProjectTaskStatus = "PENDING" | "IN_PROGRESS" | "COMPLETED";

export type Status = ProjectTaskStatus;

export type Task = {
  id: string;
  title: string;
  content: string;
  status: Status;
  createdAt: Date;
  tagName: string;
};

/** Response shape for POST /api/v1/add-project. */
export type Project = {
  id: string;
  name: string;
  description: string;
  createdAt: string;
};

/** A task as returned inside a POST /api/v1/add-project-with-tasks response. */
export type ProjectTask = {
  id: string;
  title: string;
  content: string;
  status: ProjectTaskStatus;
  tagName: string | null;
  createdAt: string;
};

/** Response shape for POST /api/v1/add-project-with-tasks. */
export type ProjectWithTasks = Project & {
  tasks: ProjectTask[];
};
