export type Tag = {
  id: string;
  name: string;
};

export type Status =
  | "TaskStatus.PENDING"
  | "TaskStatus.IN_PROGRESS"
  | "TaskStatus.COMPLETED";

export type Task = {
  id: string;
  title: string;
  content: string;
  status: Status;
  createdAt: Date;
  tagName: string;
};
