import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { useSEO } from "@/hooks/useSEO";
import { Link } from "react-router-dom";
import { NewProjectWithTasksForm } from "./_components/form";

/**
 * Screen: **New Project With Tasks** (`/dashboard/projects/new-with-tasks`).
 *
 * Purpose
 * -------
 * Advanced create flow that mirrors ``POST /api/v1/add-project-with-tasks``.
 * Collects a project plus 1..50 tasks in a single submission; each task
 * row owns its own validation, and the backend's atomic compensation
 * pattern guarantees that a partial failure leaves nothing behind.
 */
export const DashboardNewProjectWithTasksPage = () => {
  useSEO("New project with tasks | TodoApp");

  return (
    <div className="max-w-3xl mx-auto">
      <header className="mb-6">
        <h1 className="text-2xl font-bold tracking-tight">
          New project with tasks
        </h1>
        <p className="text-muted-foreground">
          Create a project and seed it with initial tasks in one atomic
          request. Need just a project?{" "}
          <Link
            to="/dashboard/projects/new"
            className="underline underline-offset-4"
          >
            Use the simple form
          </Link>
          .
        </p>
      </header>

      <Card>
        <CardHeader>
          <CardTitle>Project &amp; initial tasks</CardTitle>
          <CardDescription>
            Task titles must be unique within the request (case-insensitive).
            Tags are optional per task.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <NewProjectWithTasksForm />
        </CardContent>
      </Card>
    </div>
  );
};
