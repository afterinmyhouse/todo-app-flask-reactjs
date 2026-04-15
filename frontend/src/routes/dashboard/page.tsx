import { TagsSection } from "./_components/tags/section";
import { TasksSection } from "./_components/tasks/section";
import { useState } from "react";

export const DashboardHomePage = () => {
  const [selectedTag, setSelectedTag] = useState<string | null>(null);

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
        <TagsSection selectedTag={selectedTag} onSelectTag={setSelectedTag} />
      </section>

      <section>
        <TasksSection selectedTag={selectedTag} />
      </section>
    </div>
  );
};
