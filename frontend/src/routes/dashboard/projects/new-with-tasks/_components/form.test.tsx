import { describe, expect, it, vi } from "vitest";
import { screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { NewProjectWithTasksForm } from "./form";
import { renderWithProviders } from "@/test/render";

const navigateMock = vi.fn();

vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual<typeof import("react-router-dom")>(
    "react-router-dom",
  );
  return {
    ...actual,
    useNavigate: () => navigateMock,
  };
});

vi.mock("sonner", () => ({
  toast: { success: vi.fn(), error: vi.fn() },
}));

// Tags are fetched inside ``TaskRows`` via react-query; mock the query
// hook so the component never hits the network in tests.
vi.mock("@/services/queries/tags", () => ({
  useGetTagsQuery: () => ({ data: [{ id: "tag-1", name: "Work" }] }),
}));

const createProjectWithTasksMock = vi.fn();
vi.mock("@/services/api/projects", () => ({
  createProjectWithTasksAPI: (data: unknown) =>
    createProjectWithTasksMock(data),
}));

describe("NewProjectWithTasksForm", () => {
  it("renders with exactly one task row and a disabled remove button", () => {
    renderWithProviders(<NewProjectWithTasksForm />);

    expect(screen.getByLabelText(/project name/i)).toBeInTheDocument();
    const row0 = screen.getByTestId("task-row-0");
    expect(row0).toBeInTheDocument();
    expect(screen.queryByTestId("task-row-1")).not.toBeInTheDocument();

    const removeBtn = within(row0).getByRole("button", {
      name: /remove task 1/i,
    });
    expect(removeBtn).toBeDisabled();
  });

  it("appends and removes task rows via the field array", async () => {
    const user = userEvent.setup();
    renderWithProviders(<NewProjectWithTasksForm />);

    await user.click(screen.getByRole("button", { name: /add task/i }));
    expect(screen.getByTestId("task-row-1")).toBeInTheDocument();

    // With 2 rows, both remove buttons become enabled.
    const row1 = screen.getByTestId("task-row-1");
    const removeRow1 = within(row1).getByRole("button", {
      name: /remove task 2/i,
    });
    expect(removeRow1).toBeEnabled();

    await user.click(removeRow1);
    expect(screen.queryByTestId("task-row-1")).not.toBeInTheDocument();
  });

  it("shows validation errors and blocks submission when fields are blank", async () => {
    const user = userEvent.setup();
    renderWithProviders(<NewProjectWithTasksForm />);

    await user.click(
      screen.getByRole("button", { name: /create project with tasks/i }),
    );

    // Project name + task title errors both surface.
    expect(await screen.findByText(/name is required/i)).toBeInTheDocument();
    expect(await screen.findByText(/title is required/i)).toBeInTheDocument();
    expect(createProjectWithTasksMock).not.toHaveBeenCalled();
  });

  it("submits a valid payload and navigates to the hub", async () => {
    const user = userEvent.setup();
    createProjectWithTasksMock.mockResolvedValueOnce({
      id: "p1",
      name: "Launch",
      description: "",
      createdAt: "2026-01-01T00:00:00Z",
      tasks: [],
    });

    renderWithProviders(<NewProjectWithTasksForm />);

    await user.type(screen.getByLabelText(/project name/i), "Launch");
    const row0 = screen.getByTestId("task-row-0");
    await user.type(within(row0).getByLabelText(/title/i), "Kickoff");

    await user.click(
      screen.getByRole("button", { name: /create project with tasks/i }),
    );

    await waitFor(() => {
      expect(createProjectWithTasksMock).toHaveBeenCalledTimes(1);
    });
    const payload = createProjectWithTasksMock.mock.calls[0][0];
    expect(payload.name).toBe("Launch");
    expect(payload.tasks).toHaveLength(1);
    expect(payload.tasks[0].title).toBe("Kickoff");
    expect(payload.tasks[0].status).toBe("PENDING");

    await waitFor(() => {
      expect(navigateMock).toHaveBeenCalledWith("/dashboard/projects");
    });
  });
});
