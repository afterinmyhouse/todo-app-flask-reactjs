import { afterEach, describe, expect, it } from "vitest";
import { queryClient } from "@/lib/query-client";
import { projectsQueryKey } from "@/services/queries/projects";
import { useAuthStore } from "./auth-store";

const aliceProject = {
  id: "p1",
  name: "Alice secret roadmap",
  description: "Internal Q3 plan",
  createdAt: "2026-01-01T00:00:00Z",
};

describe("auth store query cache isolation", () => {
  afterEach(() => {
    queryClient.clear();
    useAuthStore.setState({ token: null, isLoggedIn: false });
    localStorage.removeItem("session");
  });

  it("drops cached workspace data on logout so the next session cannot see it", () => {
    useAuthStore.getState().login("alice-token");
    queryClient.setQueryData(projectsQueryKey, [aliceProject]);
    queryClient.setQueryData(["tasks"], [
      {
        id: "t1",
        title: "Alice private task",
        content: "do not leak",
        status: "PENDING",
      },
    ]);

    useAuthStore.getState().logout();

    expect(queryClient.getQueryData(projectsQueryKey)).toBeUndefined();
    expect(queryClient.getQueryData(["tasks"])).toBeUndefined();
    expect(useAuthStore.getState().isLoggedIn).toBe(false);
    expect(useAuthStore.getState().token).toBeNull();
  });

  it("clears leftover cache on login so a second user does not inherit the previous session", () => {
    queryClient.setQueryData(projectsQueryKey, [aliceProject]);

    useAuthStore.getState().login("bob-token");

    expect(queryClient.getQueryData(projectsQueryKey)).toBeUndefined();
    expect(useAuthStore.getState().token).toBe("bob-token");
    expect(useAuthStore.getState().isLoggedIn).toBe(true);
  });
});
