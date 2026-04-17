import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";

/**
 * Shown on the Projects hub when the cached projects list is empty.
 *
 * Until the backend exposes a ``GET /api/v1/projects`` endpoint, the
 * hub list is fed by create mutations only — so a cold visit always
 * lands here. The component is kept small and a11y-friendly
 * (role=region, descriptive heading) so it can be asserted in tests.
 */
export const ProjectsEmptyState = () => {
  return (
    <div
      role="region"
      aria-labelledby="projects-empty-heading"
      className="flex items-center flex-col justify-center text-center border border-dashed rounded-md w-full py-10 px-6 md:max-w-xl md:mx-auto"
    >
      <h2 id="projects-empty-heading" className="font-semibold">
        No projects yet
      </h2>
      <p className="text-muted-foreground text-sm mb-6">
        Start a lightweight project, or bootstrap one pre-filled with initial
        tasks.
      </p>
      <div className="flex flex-wrap gap-2 justify-center">
        <Button asChild>
          <Link to="/dashboard/projects/new">Create project</Link>
        </Button>
        <Button asChild variant="outline">
          <Link to="/dashboard/projects/new-with-tasks">
            Create project with tasks
          </Link>
        </Button>
      </div>
    </div>
  );
};
