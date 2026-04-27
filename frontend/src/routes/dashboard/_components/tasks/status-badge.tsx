import { Status } from "@/types/types";

interface IProps {
  status: Status;
}

export const StatusBadge = ({ status }: IProps) => {
  const STATUS_NAME: Record<Status, string> = {
    PENDING: "Pending",
    IN_PROGRESS: "In Progress",
    COMPLETED: "Completed",
  };

  const label = STATUS_NAME[status] ?? status;

  return (
    <div className="px-3 py-2 rounded-md bg-muted">
      <p className="text-xs font-medium">{label}</p>
    </div>
  );
};
