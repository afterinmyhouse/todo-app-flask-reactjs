import { TagsSection } from "./_components/tags/section";
import { TasksSection } from "./_components/tasks/section";
import type { Dispatch, SetStateAction } from "react";
import { useState } from "react";

export const DashboardHomePage = () => {
  const [selectedTag, setSelectedTag] = useState<string | null>(null);

  // Some TS/JSX tooling can lose the inferred prop types across module boundaries.
  // These casts are a small, localized fix to keep this file type-safe and quiet.
  const Tags = TagsSection as unknown as React.ComponentType<{
    selectedTag: string | null;
    onSelectTag: Dispatch<SetStateAction<string | null>>;
  }>;
  const Tasks = TasksSection as unknown as React.ComponentType<{
    selectedTag: string | null;
  }>;

  return (
    <div className="space-y-6">
      <header className="space-y-1">
        <h1 className="text-2xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground">
          Browse tags and manage your tasks in one place.
        </p>
      </header>

      <section className="space-y-3">
        <div className="flex items-center justify-between gap-4">
          <h2 className="font-semibold">Tags</h2>
          {selectedTag ? (
            <button
              type="button"
              className="text-sm text-muted-foreground hover:underline"
              onClick={() => setSelectedTag(null)}
            >
              Clear filter
            </button>
          ) : null}
        </div>
        <Tags selectedTag={selectedTag} onSelectTag={setSelectedTag} />
      </section>

      <section>
        <Tasks selectedTag={selectedTag} />
      </section>
    </div>
  );
};
