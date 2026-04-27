import { describe, expect, it } from "vitest";
import { formatEntitySearchResults } from "./entity-search";

describe("formatEntitySearchResults", () => {
  it("formats empty results", () => {
    const text = formatEntitySearchResults({
      query: "zzz",
      results: { tags: [], tasks: [], projects: [] },
    });
    expect(text).toMatch(/No matches/i);
    expect(text).toContain("zzz");
  });

  it("lists tasks tags and projects", () => {
    const text = formatEntitySearchResults({
      query: "meet",
      results: {
        tags: [{ id: "1", name: "Meetings" }],
        tasks: [
          {
            id: "t1",
            title: "Prep",
            status: "PENDING",
            tagName: "Meetings",
            snippet: "Agenda",
          },
        ],
        projects: [{ id: "p1", name: "Roadmap", description: "Q2" }],
      },
    });
    expect(text).toMatch(/Tasks/i);
    expect(text).toMatch(/Tags/i);
    expect(text).toMatch(/Projects/i);
    expect(text).toContain("Prep");
    expect(text).toContain("Meetings");
    expect(text).toContain("Roadmap");
  });
});
