import { describe, expect, it, vi } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { NewProjectForm } from "./form";
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

const createProjectMock = vi.fn();
vi.mock("@/services/api/projects", () => ({
  createProjectAPI: (data: unknown) => createProjectMock(data),
}));

describe("NewProjectForm", () => {
  it("renders name + description fields and submit button", () => {
    renderWithProviders(<NewProjectForm />);

    expect(screen.getByLabelText(/name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/description/i)).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /create project/i }),
    ).toBeInTheDocument();
  });

  it("blocks submission and shows a validation error when name is blank", async () => {
    const user = userEvent.setup();
    renderWithProviders(<NewProjectForm />);

    await user.click(screen.getByRole("button", { name: /create project/i }));

    expect(await screen.findByText(/name is required/i)).toBeInTheDocument();
    expect(createProjectMock).not.toHaveBeenCalled();
  });

  it("submits valid data, calls the API, and navigates to the hub", async () => {
    const user = userEvent.setup();
    createProjectMock.mockResolvedValueOnce({
      id: "p1",
      name: "Roadmap",
      description: "Plan",
      createdAt: "2026-01-01T00:00:00Z",
    });

    renderWithProviders(<NewProjectForm />);

    await user.type(screen.getByLabelText(/name/i), "Roadmap");
    await user.type(screen.getByLabelText(/description/i), "Plan");
    await user.click(screen.getByRole("button", { name: /create project/i }));

    await waitFor(() => {
      expect(createProjectMock).toHaveBeenCalledWith({
        name: "Roadmap",
        description: "Plan",
      });
    });
    await waitFor(() => {
      expect(navigateMock).toHaveBeenCalledWith("/dashboard/projects");
    });
  });
});
