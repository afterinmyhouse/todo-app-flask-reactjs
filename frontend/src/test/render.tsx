import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, RenderOptions } from "@testing-library/react";
import { ReactElement, ReactNode } from "react";
import { MemoryRouter } from "react-router-dom";

/**
 * Test helper that wraps a rendered element in the same providers the
 * real app uses (React Query + React Router). Each call builds a fresh
 * ``QueryClient`` with retries disabled so mutation failures surface
 * immediately in assertions.
 */
type WrapperOptions = {
  route?: string;
  queryClient?: QueryClient;
};

export const buildQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

export const renderWithProviders = (
  ui: ReactElement,
  {
    route = "/",
    queryClient = buildQueryClient(),
    ...options
  }: WrapperOptions & Omit<RenderOptions, "wrapper"> = {},
) => {
  const Wrapper = ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={[route]}>{children}</MemoryRouter>
    </QueryClientProvider>
  );

  return {
    queryClient,
    ...render(ui, { wrapper: Wrapper, ...options }),
  };
};
