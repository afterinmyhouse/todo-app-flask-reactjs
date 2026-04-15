import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { SignInForm } from "./form";

// Minimal mocks so the component can render in isolation.
vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual<typeof import("react-router-dom")>(
    "react-router-dom",
  );
  return {
    ...actual,
    useNavigate: () => vi.fn(),
  };
});

vi.mock("@/stores/auth-store", () => ({
  useAuthStore: () => ({ login: vi.fn() }),
}));

vi.mock("@/services/api/client", () => ({
  api: { post: vi.fn() },
}));

describe("SignInForm", () => {
  it("renders email + password fields and submit button", () => {
    render(<SignInForm />);

    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /sign in/i }),
    ).toBeInTheDocument();
  });

  it("submits form (skeleton)", async () => {
    const user = userEvent.setup();
    render(<SignInForm />);

    await user.type(screen.getByLabelText(/email/i), "user@example.com");
    await user.type(screen.getByLabelText(/password/i), "password");
    await user.click(screen.getByRole("button", { name: /sign in/i }));

    // TODO: assert axios.post called with expected URL + payload
    // TODO: assert login(token) called and navigation to /dashboard happens on success
    expect(true).toBe(true);
  });
});

