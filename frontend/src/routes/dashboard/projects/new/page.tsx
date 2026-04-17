import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { useSEO } from "@/hooks/useSEO";
import { Link } from "react-router-dom";
import { NewProjectForm } from "./_components/form";

/**
 * Screen: **New Project** (`/dashboard/projects/new`).
 *
 * Purpose
 * -------
 * Thin single-entity create screen that hosts ``NewProjectForm``. Kept
 * presentational so ``NewProjectForm`` can be unit-tested in isolation
 * (see ``./_components/form.test.tsx``).
 */
export const DashboardNewProjectPage = () => {
  useSEO("New project | TodoApp");

  return (
    <div className="max-w-2xl mx-auto">
      <header className="mb-6">
        <h1 className="text-2xl font-bold tracking-tight">New project</h1>
        <p className="text-muted-foreground">
          Need to seed initial tasks in the same request? Use{" "}
          <Link
            to="/dashboard/projects/new-with-tasks"
            className="underline underline-offset-4"
          >
            New project with tasks
          </Link>{" "}
          instead.
        </p>
      </header>

      <Card>
        <CardHeader>
          <CardTitle>Project details</CardTitle>
          <CardDescription>
            Names must be unique per user (case-insensitive).
          </CardDescription>
        </CardHeader>
        <CardContent>
          <NewProjectForm />
        </CardContent>
      </Card>
    </div>
  );
};
