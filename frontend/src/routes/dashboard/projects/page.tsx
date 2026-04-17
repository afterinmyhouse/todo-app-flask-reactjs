import { Button } from "@/components/ui/button";
import { useSEO } from "@/hooks/useSEO";
import { useGetProjectsQuery } from "@/services/queries/projects";
import { Link } from "react-router-dom";
import { ProjectCard } from "./_components/project-card";
import { ProjectsEmptyState } from "./_components/empty-state";

/**
 * Screen: **Projects hub** (`/dashboard/projects`).
 *
 * Purpose
 * -------
 * - Lists the user's projects (currently sourced from the React Query
 *   cache populated by the create mutations; see
 *   ``src/services/queries/projects.ts`` for the migration path to a
 *   real ``GET /api/v1/projects`` endpoint).
 * - Provides entry points to the two project-creation flows.
 *
 * Data shape
 * ----------
 * Consumes ``Project[]`` from ``useGetProjectsQuery``. Renders
 * ``ProjectsEmptyState`` when the list is empty.
 */
export const DashboardProjectsPage = () => {
  useSEO("Projects | TodoApp");

  const { data: projects = [] } = useGetProjectsQuery();

  return (
    <div className="space-y-6">
      <header className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div className="space-y-1">
          <h1 className="text-2xl font-bold tracking-tight">Projects</h1>
          <p className="text-muted-foreground">
            Organize work into projects. Create one on its own or seed it with
            initial tasks in a single atomic request.
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button asChild>
            <Link to="/dashboard/projects/new">New project</Link>
          </Button>
          <Button asChild variant="outline">
            <Link to="/dashboard/projects/new-with-tasks">New with tasks</Link>
          </Button>
        </div>
      </header>

      {projects.length === 0 ? (
        <ProjectsEmptyState />
      ) : (
        <div className="grid grid-cols-1 gap-3 md:grid-cols-2 lg:grid-cols-3">
          {projects.map((project) => (
            <ProjectCard key={project.id} project={project} />
          ))}
        </div>
      )}
    </div>
  );
};
