import { describe, expect, it } from "vitest";
import { getOpeningMessage, getReply } from "./assistant-agent";

describe("getOpeningMessage", () => {
  it("welcomes anonymous users on home", () => {
    const text = getOpeningMessage({ pathname: "/", isAuthenticated: false });
    expect(text).toMatch(/sign in|create an account/i);
    expect(text).toMatch(/browser/i);
  });

  it("describes dashboard for signed-in users", () => {
    const text = getOpeningMessage({
      pathname: "/dashboard",
      isAuthenticated: true,
    });
    expect(text).toMatch(/dashboard|tags|tasks/i);
  });

  it("hints bulk project flow", () => {
    const text = getOpeningMessage({
      pathname: "/dashboard/projects/new-with-tasks",
      isAuthenticated: true,
    });
    expect(text).toMatch(/50|tasks|project/i);
  });
});

describe("getReply", () => {
  it("warns on password-related queries", () => {
    const r = getReply("What is my password?", {
      pathname: "/dashboard",
      isAuthenticated: true,
    });
    expect(r).toMatch(/never paste|sign-in form/i);
  });

  it("explains tags", () => {
    const r = getReply("How do tags work?", {
      pathname: "/dashboard",
      isAuthenticated: true,
    });
    expect(r).toMatch(/tags/i);
  });

  it("falls back with unknown input", () => {
    const r = getReply("xyzabc123", {
      pathname: "/dashboard/settings",
      isAuthenticated: true,
    });
    expect(r).toMatch(/keywords|tasks|tags|projects/i);
  });
});
