import { useGetTagsQuery } from "@/services/queries/tags";
import { LoadingState } from "./loading-state";
import { cn } from "@/lib/utils";
import { Tag } from "lucide-react";

type Props = {
  selectedTag: string | null;
  onSelectTag: (tagName: string | null) => void;
};

export function TagsSection({ selectedTag, onSelectTag }: Props) {
  const { data: tags = [], isLoading } = useGetTagsQuery();

  if (isLoading) return <LoadingState />;

  const chipBase =
    "shrink-0 rounded-md border bg-background px-3 py-2 text-xs font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring";

  return (
    <div
      className={cn(
        // Mobile: horizontal scroll “chips bar”
        "flex items-center gap-2 overflow-x-auto pb-2",
        // Hide scrollbar without requiring a plugin
        "[-ms-overflow-style:none] [scrollbar-width:none] [&::-webkit-scrollbar]:hidden",
        // md+: switch to a grid for easier scanning
        "md:grid md:grid-cols-6 md:gap-2 md:overflow-visible md:pb-0",
      )}
    >
      <button
        type="button"
        className={cn(
          chipBase,
          selectedTag === null
            ? "bg-accent text-accent-foreground"
            : "hover:bg-accent hover:text-accent-foreground",
        )}
        onClick={() => onSelectTag(null)}
      >
        All
      </button>

      {tags.map((tag) => (
        <button
          key={tag.id}
          type="button"
          className={cn(
            chipBase,
            selectedTag === tag.name
              ? "bg-accent text-accent-foreground"
              : "hover:bg-accent hover:text-accent-foreground",
          )}
          onClick={() => onSelectTag(tag.name)}
        >
          <span className="inline-flex items-center gap-2">
            <Tag className="size-4" />
            {tag.name}
          </span>
        </button>
      ))}
    </div>
  );
}
