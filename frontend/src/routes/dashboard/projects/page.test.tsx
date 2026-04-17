import { describe, expect, it, vi } from "vitest";
import { screen } from "@testing-library/react";
import { DashboardProjectsPage } from "./page";
import { buildQueryClient, renderWithProviders } from "@/test/render";
import { projectsQueryKey } from "@/services/queries/projects";
import type { Project } from "@/types/types";

// Silence toasts in tests; the hub doesn't use them directly but
// downstream mutations might.
vi.mock("sonner", () => ({ toast: { success: vi.fn(), error: vi.fn() } }));

describe("DashboardProjectsPage", () => {
  it("renders the empty state with both CTAs when cache is empty", () => {
    renderWithProviders(<DashboardProjectsPage />, {
      route: "/dashboard/projects",
    });

    expect(
      screen.getByRole("heading", { level: 1, name: /projects/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("heading", { level: 2, name: /no projects yet/i }),
    ).toBeInTheDocument();

    // CTAs appear both in the header and inside the empty state.
    expect(
      screen.getAllByRole("link", { name: /new project$/i }).length,
    ).toBeGreaterThanOrEqual(1);
    expect(
      screen.getAllByRole("link", { name: /new with tasks|new project with tasks/i })
        .length,
    ).toBeGreaterThanOrEqual(1);
  });

  it("renders cached projects instead of the empty state", () => {
    const queryClient = buildQueryClient();
    const seeded: Project[] = [
      {
        id: "p1",
        name: "Roadmap",
        description: "Quarterly planning board",
        createdAt: "2026-01-02T03:04:05Z",
      },
      {
        id: "p2",
        name: "Launch",
        description: "",
        createdAt: "2026-01-03T03:04:05Z",
      },
    ];
    queryClient.setQueryData(projectsQueryKey, seeded);

    renderWithProviders(<DashboardProjectsPage />, {
      route: "/dashboard/projects",
      queryClient,
    });

    expect(screen.getByText("Roadmap")).toBeInTheDocument();
    expect(screen.getByText("Launch")).toBeInTheDocument();
    expect(screen.queryByText(/no projects yet/i)).not.toBeInTheDocument();
  });
});
