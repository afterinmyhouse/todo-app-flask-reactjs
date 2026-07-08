import { describe, expect, it, beforeEach, vi } from "vitest";
import { act, screen } from "@testing-library/react";
import { Route, Routes } from "react-router-dom";
import { DashboardRoot } from "./dashboard/root";
import { LandingRoot } from "./landing/root";
import { useAuthStore } from "@/stores/auth-store";
import { renderWithProviders } from "@/test/render";

vi.mock("@/services/api/auth", () => ({
  fetchCurrentUser: vi.fn().mockResolvedValue({
    id: "user-1",
    username: "user",
    email: "user@example.com",
  }),
}));

vi.mock("@/components/assistant/assistant-widget", () => ({
  AssistantWidget: () => null,
}));

vi.mock("sonner", () => ({
  Toaster: () => null,
}));

describe("route roots", () => {
  beforeEach(() => {
    localStorage.clear();
    useAuthStore.setState({ token: null, isLoggedIn: false });
  });

  it("keeps dashboard hooks stable when auth is cleared in place", async () => {
    act(() => {
      useAuthStore.getState().login("token");
    });

    renderWithProviders(
      <Routes>
        <Route path="/" element={<div>Landing redirect target</div>} />
        <Route path="/dashboard" element={<DashboardRoot />}>
          <Route index element={<div>Dashboard content</div>} />
        </Route>
      </Routes>,
      { route: "/dashboard" },
    );

    expect(screen.getByText("Dashboard content")).toBeInTheDocument();

    act(() => {
      useAuthStore.getState().logout();
    });

    expect(await screen.findByText("Landing redirect target")).toBeInTheDocument();
  });

  it("keeps landing hooks stable when auth is set in place", async () => {
    renderWithProviders(
      <Routes>
        <Route path="/" element={<LandingRoot />}>
          <Route index element={<div>Landing content</div>} />
        </Route>
        <Route path="/dashboard" element={<div>Dashboard redirect target</div>} />
      </Routes>,
    );

    expect(screen.getByText("Landing content")).toBeInTheDocument();

    act(() => {
      useAuthStore.getState().login("token");
    });

    expect(await screen.findByText("Dashboard redirect target")).toBeInTheDocument();
  });
});
