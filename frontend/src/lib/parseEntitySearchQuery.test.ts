/**
 * Under test — `parseEntitySearchQuery` from `./entity-search.ts`:
 *
 * ```ts
 * const SEARCH_INTENT = /^\s*(search|find)\s+(.+)$/i;
 *
 * export function parseEntitySearchQuery(message: string): string | null {
 *   const m = message.trim().match(SEARCH_INTENT);
 *   const raw = m?.[2]?.trim() ?? "";
 *   if (raw.length < 2) return null;
 *   return raw.length > 120 ? raw.slice(0, 120) : raw;
 * }
 * ```
 */

import { describe, expect, it } from "vitest";
import { parseEntitySearchQuery } from "./entity-search";

describe("parseEntitySearchQuery", () => {
  it("parses standard search command with a single term", () => {
    expect(parseEntitySearchQuery("search meeting")).toBe("meeting");
  });

  it("parses find command case-insensitively with extra surrounding whitespace", () => {
    expect(parseEntitySearchQuery("  FiNd  invoice draft  ")).toBe("invoice draft");
  });

  it("accepts exactly two characters as the minimum valid query", () => {
    expect(parseEntitySearchQuery("search ab")).toBe("ab");
  });

  // Edge: no keyword match, empty message, or captured segment still under 2 chars after trim.
  it("returns null when there is no intent, empty input, or query shorter than two characters", () => {
    expect(parseEntitySearchQuery("hello world")).toBeNull();
    expect(parseEntitySearchQuery("")).toBeNull();
    expect(parseEntitySearchQuery("search a")).toBeNull();
    expect(parseEntitySearchQuery("find x ")).toBeNull();
  });

  // Edge: long pasted strings are capped so API `q` stays within backend MAX_QUERY_LEN alignment.
  it("truncates queries longer than 120 characters to 120", () => {
    const long = "x".repeat(130);
    expect(parseEntitySearchQuery(`search ${long}`)?.length).toBe(120);
    expect(parseEntitySearchQuery(`search ${long}`)).toBe(long.slice(0, 120));
  });
});
