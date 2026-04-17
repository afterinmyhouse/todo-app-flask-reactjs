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
  CreateProjectSchema,
  TCreateProjectSchema,
} from "@/schemas/project-schema";
import { useCreateProjectMutation } from "@/services/mutations/projects";
import { zodResolver } from "@hookform/resolvers/zod";
import { AxiosError } from "axios";
import { LoaderCircle } from "lucide-react";
import { useForm } from "react-hook-form";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";

/**
 * Form for POST /api/v1/add-project.
 *
 * Component boundaries match the existing ``SignInForm`` conventions:
 * the form owns its own submission handler so the parent screen stays
 * purely presentational and simpler to unit-test.
 */
export const NewProjectForm = () => {
  const navigate = useNavigate();
  const mutation = useCreateProjectMutation();
  const form = useForm<TCreateProjectSchema>({
    resolver: zodResolver(CreateProjectSchema),
    defaultValues: { name: "", description: "" },
  });

  const {
    handleSubmit,
    control,
    formState: { isSubmitting },
  } = form;

  const onSubmit = async (formData: TCreateProjectSchema) => {
    try {
      await mutation.mutateAsync(formData);
      toast.success("Project created");
      navigate("/dashboard/projects");
    } catch (err) {
      if (err instanceof AxiosError) {
        toast.error(getApiErrorMessage(err.response?.data));
      } else {
        toast.error("Something went wrong");
      }
    }
  };

  return (
    <Form {...form}>
      <form className="grid gap-y-4" onSubmit={handleSubmit(onSubmit)}>
        <FormField
          control={control}
          name="name"
          render={({ field }) => (
            <FormItem className="space-y-1">
              <FormLabel>Name</FormLabel>
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
              <FormLabel>Description</FormLabel>
              <FormControl>
                <Textarea
                  {...field}
                  autoComplete="off"
                  className="resize-none"
                  rows={4}
                  disabled={isSubmitting}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <div className="flex justify-end">
          <Button type="submit" className="font-medium" disabled={isSubmitting}>
            {isSubmitting ? (
              <LoaderCircle className="size-5 animate-spin" />
            ) : (
              "Create project"
            )}
          </Button>
        </div>
      </form>
    </Form>
  );
};
