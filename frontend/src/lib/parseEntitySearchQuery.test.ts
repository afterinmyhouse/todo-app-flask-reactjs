/**
 * Under test — `parseEntitySearchQuery` in `./entity-search.ts` (uses
 * `ENTITY_SEARCH_QUERY_MIN_LEN` / `ENTITY_SEARCH_QUERY_MAX_LEN`).
 */

import { describe, expect, it } from "vitest";
import {
  ENTITY_SEARCH_QUERY_MAX_LEN,
  ENTITY_SEARCH_QUERY_MIN_LEN,
  parseEntitySearchQuery,
} from "./entity-search";

const belowMin = "a".repeat(Math.max(1, ENTITY_SEARCH_QUERY_MIN_LEN - 1));

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

  it("accepts a three-character query above the minimum length", () => {
    expect(parseEntitySearchQuery("search abc")).toBe("abc");
  });

  // Edge: no keyword match, empty message, or captured segment below `ENTITY_SEARCH_QUERY_MIN_LEN`.
  it("returns null when there is no intent, empty input, or query shorter than two characters", () => {
    expect(parseEntitySearchQuery("hello world")).toBeNull();
    expect(parseEntitySearchQuery("")).toBeNull();
    expect(parseEntitySearchQuery(`search ${belowMin}`)).toBeNull();
    expect(parseEntitySearchQuery("find x ")).toBeNull();
  });

  // Edge: long pasted strings are capped so API `q` stays within backend max length.
  it("truncates queries longer than 120 characters to 120", () => {
    const long = "x".repeat(130);
    expect(parseEntitySearchQuery(`search ${long}`)?.length).toBe(
      ENTITY_SEARCH_QUERY_MAX_LEN,
    );
    expect(parseEntitySearchQuery(`search ${long}`)).toBe(
      long.slice(0, ENTITY_SEARCH_QUERY_MAX_LEN),
    );
  });

  // Edge: exactly one character over the max — catches wrong slice length or `>=` vs `>`.
  it("truncates when the raw segment is exactly one character over the max length", () => {
    const raw = "y".repeat(ENTITY_SEARCH_QUERY_MAX_LEN + 1);
    const out = parseEntitySearchQuery(`find ${raw}`);
    expect(out?.length).toBe(ENTITY_SEARCH_QUERY_MAX_LEN);
    expect(out).toBe(raw.slice(0, ENTITY_SEARCH_QUERY_MAX_LEN));
  });

  it("does not truncate when the raw segment length equals the max length", () => {
    const raw = "z".repeat(ENTITY_SEARCH_QUERY_MAX_LEN);
    expect(parseEntitySearchQuery(`search ${raw}`)).toBe(raw);
  });
});
