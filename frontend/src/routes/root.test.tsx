import { act, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { Route, Routes } from "react-router-dom";
import { DashboardRoot } from "./dashboard/root";
import { LandingRoot } from "./landing/root";
import { renderWithProviders } from "@/test/render";
import { useAuthStore } from "@/stores/auth-store";

vi.mock("@/services/api/auth", () => ({
  fetchCurrentUser: vi.fn(() =>
    Promise.resolve({ id: "u1", username: "user", email: "user@example.com" }),
  ),
}));

const RootRoutes = () => (
  <Routes>
    <Route path="/" element={<LandingRoot />}>
      <Route index element={<div>Landing home</div>} />
    </Route>
    <Route path="/dashboard" element={<DashboardRoot />}>
      <Route index element={<div>Dashboard home</div>} />
    </Route>
  </Routes>
);

describe("route roots", () => {
  beforeEach(() => {
    localStorage.clear();
    useAuthStore.setState({ token: null, isLoggedIn: false });
    vi.clearAllMocks();
  });

  it("redirects out of the dashboard after logout without changing hook order", async () => {
    useAuthStore.getState().login("valid-token");

    renderWithProviders(<RootRoutes />, { route: "/dashboard" });

    expect(screen.getByText("Dashboard home")).toBeInTheDocument();

    await act(async () => {
      useAuthStore.getState().logout();
    });

    await waitFor(() => {
      expect(screen.getByText("Landing home")).toBeInTheDocument();
    });
  });

  it("redirects from landing after login without changing hook order", async () => {
    renderWithProviders(<RootRoutes />, { route: "/" });

    expect(screen.getByText("Landing home")).toBeInTheDocument();

    await act(async () => {
      useAuthStore.getState().login("valid-token");
    });

    await waitFor(() => {
      expect(screen.getByText("Dashboard home")).toBeInTheDocument();
    });
  });
});
