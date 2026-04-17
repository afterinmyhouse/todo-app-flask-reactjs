import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { Project } from "@/types/types";

type Props = {
  project: Project;
};

/** Compact read-only summary used in the Projects hub list. */
export const ProjectCard = ({ project }: Props) => {
  const createdAt = new Date(project.createdAt);

  return (
    <Card className="hover:shadow-sm transition-shadow">
      <CardHeader className="pb-2">
        <CardTitle className="truncate">{project.name}</CardTitle>
      </CardHeader>
      <CardContent className="text-sm text-muted-foreground space-y-2">
        {project.description ? (
          <p className="line-clamp-3">{project.description}</p>
        ) : (
          <p className="italic">No description</p>
        )}
        <p className="text-xs">
          Created{" "}
          <time dateTime={project.createdAt}>
            {isNaN(createdAt.getTime()) ? project.createdAt : createdAt.toLocaleString()}
          </time>
        </p>
      </CardContent>
    </Card>
  );
};
