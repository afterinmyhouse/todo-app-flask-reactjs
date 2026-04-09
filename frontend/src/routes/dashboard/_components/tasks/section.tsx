import { useGetTasksOnUserQuery } from "@/services/queries/tasks";
import { EmptyState } from "./empty-state";
import { CreateDialog } from "./create-dialog";
import { TaskCard } from "./card";
import { useMemo } from "react";

type Props = {
  selectedTag: string | null;
};

export function TasksSection({ selectedTag }: Props) {
  const { data: tasks = [] } = useGetTasksOnUserQuery();

  const filteredTasks = useMemo(() => {
    if (!selectedTag) return tasks;
    return tasks.filter((t) => t.tagName === selectedTag);
  }, [tasks, selectedTag]);

  return (
    <div>
      <div className="flex items-center justify-between gap-4 mb-4">
        <div>
          <h2 className="font-semibold">Tasks</h2>
          <p className="text-sm text-muted-foreground">
            {selectedTag ? `Filtered by “${selectedTag}”` : "All tasks"}
          </p>
        </div>
        <div className="w-full sm:w-auto sm:shrink-0">
          <CreateDialog />
        </div>
      </div>

      {filteredTasks.length === 0 ? (
        <EmptyState />
      ) : (
        <div className="grid grid-cols-1 gap-3 md:grid-cols-2 lg:grid-cols-3">
          {filteredTasks.map((task) => (
            <TaskCard key={task.id} task={task} />
          ))}
        </div>
      )}
    </div>
  );
}
