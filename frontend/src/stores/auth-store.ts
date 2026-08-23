import { queryClient } from "@/lib/query-client";
import { create } from "zustand";
import { persist } from "zustand/middleware";

type State = {
  token: string | null;
  isLoggedIn: boolean;
};

type Action = {
  /** Persist JWT and mark the session active (used after login or register). */
  login: (token: string) => void;
  logout: () => void;
};

export const useAuthStore = create<State & Action>()(
  persist(
    (set) => ({
      token: null,
      isLoggedIn: false,
      login: (token: string) => {
        // Queries are not user-scoped. Drop the previous session's cache
        // before activating this token so a second user on the same tab
        // cannot read leftover tasks/projects.
        queryClient.clear();
        set({ token, isLoggedIn: true });
      },
      logout: () => {
        set({ token: null, isLoggedIn: false });
        queryClient.clear();
      },
    }),
    { name: "session" },
  ),
);
