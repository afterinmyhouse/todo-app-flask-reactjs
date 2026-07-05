import { act, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { DashboardRoot } from "./dashboard/root";
import { LandingRoot } from "./landing/root";
import { useAuthStore } from "@/stores/auth-store";
import { renderWithProviders } from "@/test/render";

vi.mock("@/components/assistant/assistant-widget", () => ({
  AssistantWidget: () => <div data-testid="assistant-widget" />,
}));

vi.mock("@/services/api/auth", () => ({
  fetchCurrentUser: vi.fn(() => Promise.resolve({ id: "user-1" })),
}));

vi.mock("sonner", () => ({
  Toaster: () => null,
}));

describe("route root auth guards", () => {
  beforeEach(() => {
    localStorage.clear();
    useAuthStore.setState({ isLoggedIn: false, token: null });
  });

  it("keeps DashboardRoot hook order stable when a session logs out", () => {
    useAuthStore.setState({ isLoggedIn: true, token: "token" });
    renderWithProviders(<DashboardRoot />, { route: "/dashboard" });

    expect(screen.getByRole("button", { name: /logout/i })).toBeInTheDocument();

    expect(() => {
      act(() => {
        useAuthStore.setState({ isLoggedIn: false, token: null });
      });
    }).not.toThrow();
  });

  it("keeps LandingRoot hook order stable when a session logs in", () => {
    renderWithProviders(<LandingRoot />, { route: "/" });

    expect(screen.getByText("TodoApp")).toBeInTheDocument();

    expect(() => {
      act(() => {
        useAuthStore.setState({ isLoggedIn: true, token: "token" });
      });
    }).not.toThrow();
  });
});
