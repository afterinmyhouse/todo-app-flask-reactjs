import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { getApiErrorMessage } from "@/lib/utils";
import {
  CreateProjectWithTasksSchema,
  TCreateProjectWithTasksSchema,
} from "@/schemas/project-schema";
import { useCreateProjectWithTasksMutation } from "@/services/mutations/projects";
import { zodResolver } from "@hookform/resolvers/zod";
import { AxiosError } from "axios";
import { LoaderCircle, Plus } from "lucide-react";
import { useFieldArray, useForm } from "react-hook-form";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { TaskRows } from "./task-rows";

/**
 * Default values for one task row. Exported so tests and callers that
 * pre-seed the form (e.g. "duplicate project") stay in sync.
 */
export const EMPTY_TASK: TCreateProjectWithTasksSchema["tasks"][number] = {
  title: "",
  content: "",
  status: "PENDING",
  tagId: "",
};

export const NewProjectWithTasksForm = () => {
  const navigate = useNavigate();
  const mutation = useCreateProjectWithTasksMutation();
  const form = useForm<TCreateProjectWithTasksSchema>({
    resolver: zodResolver(CreateProjectWithTasksSchema),
    defaultValues: {
      name: "",
      description: "",
      tasks: [EMPTY_TASK],
    },
    mode: "onSubmit",
  });

  const {
    handleSubmit,
    control,
    formState: { isSubmitting, errors },
  } = form;

  const { fields, append, remove } = useFieldArray({
    control,
    name: "tasks",
  });

  const onSubmit = async (formData: TCreateProjectWithTasksSchema) => {
    try {
      await mutation.mutateAsync(formData);
      toast.success("Project created with tasks");
      navigate("/dashboard/projects");
    } catch (err) {
      if (err instanceof AxiosError) {
        toast.error(getApiErrorMessage(err.response?.data));
      } else {
        toast.error("Something went wrong");
      }
    }
  };

  // Surface the array-level error (min/max/empty) once, above the list.
  const tasksArrayError =
    errors.tasks && !Array.isArray(errors.tasks)
      ? (errors.tasks as { message?: string }).message
      : undefined;

  return (
    <Form {...form}>
      <form className="grid gap-y-6" onSubmit={handleSubmit(onSubmit)}>
        <section className="grid gap-y-4">
          <FormField
            control={control}
            name="name"
            render={({ field }) => (
              <FormItem className="space-y-1">
                <FormLabel>Project name</FormLabel>
                <FormControl>
                  <Input
                    {...field}
                    type="text"
                    autoComplete="off"
                    disabled={isSubmitting}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={control}
            name="description"
            render={({ field }) => (
              <FormItem className="space-y-1">
                <FormLabel>Project description</FormLabel>
                <FormControl>
                  <Textarea
                    {...field}
                    autoComplete="off"
                    className="resize-none"
                    rows={3}
                    disabled={isSubmitting}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
        </section>

        <section className="space-y-3">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="font-semibold">Initial tasks</h2>
              <p className="text-sm text-muted-foreground">
                Create at least one task. Up to 50 allowed per project.
              </p>
            </div>
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={() => append({ ...EMPTY_TASK })}
              disabled={isSubmitting || fields.length >= 50}
            >
              <Plus className="size-4 mr-1" />
              Add task
            </Button>
          </div>

          {tasksArrayError ? (
            <p
              role="alert"
              className="text-sm font-medium text-destructive"
            >
              {tasksArrayError}
            </p>
          ) : null}

          <TaskRows
            control={control}
            fields={fields}
            canRemove={fields.length > 1}
            disabled={isSubmitting}
            onRemove={remove}
          />
        </section>

        <div className="flex justify-end">
          <Button type="submit" className="font-medium" disabled={isSubmitting}>
            {isSubmitting ? (
              <LoaderCircle className="size-5 animate-spin" />
            ) : (
              "Create project with tasks"
            )}
          </Button>
        </div>
      </form>
    </Form>
  );
};
