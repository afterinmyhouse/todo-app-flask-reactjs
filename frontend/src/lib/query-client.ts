import { QueryClient } from "@tanstack/react-query";

/**
 * Process-wide React Query client.
 *
 * Workspace queries (`tasks`, `projects`, …) are not keyed by user id, so
 * this instance must be cleared whenever the signed-in account changes.
 * The auth store does that on login and logout.
 */
export const queryClient = new QueryClient();
