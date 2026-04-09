import { Task } from "@/types/types";
import { TagBadge } from "../tags/tag-badge";
import { StatusBadge } from "./status-badge";
import { ShowDialog } from "./show-dialog";
import { EditDialog } from "./edit-dialog";
import { Card, CardContent, CardHeader } from "@/components/ui/card";

interface IProps {
  task: Task;
}

export const TaskCard = ({ task }: IProps) => {
  return (
    <Card className="hover:shadow-sm transition-shadow">
      <CardHeader className="pb-3">
        <div className="flex items-center gap-2">
          <div className="min-w-0">
            <ShowDialog task={task} />
          </div>
          <EditDialog task={task} />
        </div>
      </CardHeader>
      <CardContent className="pt-0">
        <div className="flex flex-wrap items-center gap-2">
          <TagBadge name={task.tagName} />
          <StatusBadge status={task.status} />
        </div>
      </CardContent>
    </Card>
  );
};
