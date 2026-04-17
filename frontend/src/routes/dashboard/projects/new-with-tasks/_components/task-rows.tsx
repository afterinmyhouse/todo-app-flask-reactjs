import { Button } from "@/components/ui/button";
import {
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import type { TCreateProjectWithTasksSchema } from "@/schemas/project-schema";
import { useGetTagsQuery } from "@/services/queries/tags";
import { Trash2 } from "lucide-react";
import {
  Control,
  FieldArrayWithId,
} from "react-hook-form";

/**
 * Row-level UI for the ``tasks`` field array on the New Project With
 * Tasks screen.
 *
 * Split out from the top-level form so:
 * - The parent form stays short and readable.
 * - Render churn is contained when a single row re-renders.
 * - Tests can target a single row without spinning up the whole form.
 */

const NO_TAG_VALUE = "__none__";

type Props = {
  control: Control<TCreateProjectWithTasksSchema>;
  fields: FieldArrayWithId<TCreateProjectWithTasksSchema, "tasks", "id">[];
  canRemove: boolean;
  disabled: boolean;
  onRemove: (index: number) => void;
};

export const TaskRows = ({
  control,
  fields,
  canRemove,
  disabled,
  onRemove,
}: Props) => {
  const { data: tags = [] } = useGetTagsQuery();

  return (
    <ul className="space-y-4">
      {fields.map((field, index) => (
        <li
          key={field.id}
          data-testid={`task-row-${index}`}
          className="border rounded-md p-4 space-y-3 relative"
        >
          <div className="flex items-center justify-between">
            <p className="text-sm font-medium">Task {index + 1}</p>
            <Button
              type="button"
              variant="ghost"
              size="sm"
              aria-label={`Remove task ${index + 1}`}
              disabled={!canRemove || disabled}
              onClick={() => onRemove(index)}
            >
              <Trash2 className="size-4" />
            </Button>
          </div>

          <FormField
            control={control}
            name={`tasks.${index}.title` as const}
            render={({ field }) => (
              <FormItem className="space-y-1">
                <FormLabel>Title</FormLabel>
                <FormControl>
                  <Input
                    {...field}
                    type="text"
                    autoComplete="off"
                    disabled={disabled}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={control}
            name={`tasks.${index}.content` as const}
            render={({ field }) => (
              <FormItem className="space-y-1">
                <FormLabel>Content</FormLabel>
                <FormControl>
                  <Textarea
                    {...field}
                    autoComplete="off"
                    className="resize-none"
                    rows={3}
                    disabled={disabled}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <div className="grid gap-3 md:grid-cols-2">
            <FormField
              control={control}
              name={`tasks.${index}.status` as const}
              render={({ field }) => (
                <FormItem className="space-y-1">
                  <FormLabel>Status</FormLabel>
                  <Select
                    onValueChange={field.onChange}
                    value={field.value}
                    disabled={disabled}
                  >
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Select a status..." />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      <SelectItem value="PENDING">Pending</SelectItem>
                      <SelectItem value="IN_PROGRESS">In progress</SelectItem>
                      <SelectItem value="COMPLETED">Completed</SelectItem>
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={control}
              name={`tasks.${index}.tagId` as const}
              render={({ field }) => (
                <FormItem className="space-y-1">
                  <FormLabel>Tag (optional)</FormLabel>
                  <Select
                    onValueChange={(value) =>
                      field.onChange(value === NO_TAG_VALUE ? "" : value)
                    }
                    value={field.value ? field.value : NO_TAG_VALUE}
                    disabled={disabled}
                  >
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="No tag" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      <SelectItem value={NO_TAG_VALUE}>No tag</SelectItem>
                      {tags.map((tag) => (
                        <SelectItem key={tag.id} value={tag.id}>
                          {tag.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />
          </div>

        </li>
      ))}
    </ul>
  );
};
