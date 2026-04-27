import type { EntitySearchResponse } from "@/types/types";
import { getEntitySearchAPI } from "@/services/api/search";

const SEARCH_INTENT = /^\s*(search|find)\s+(.+)$/i;

/** Keep in sync with backend `SearchController` min/max query length. */
export const ENTITY_SEARCH_QUERY_MIN_LEN = 2;
export const ENTITY_SEARCH_QUERY_MAX_LEN = 120;

/**
 * If the user message is a workspace search command, returns the trimmed query
 * or null. Bounds match `GET /api/v1/search` (`ENTITY_SEARCH_QUERY_*_LEN`).
 */
export function parseEntitySearchQuery(message: string): string | null {
  const m = message.trim().match(SEARCH_INTENT);
  const raw = m?.[2]?.trim() ?? "";
  if (raw.length < ENTITY_SEARCH_QUERY_MIN_LEN) return null;
  return raw.length > ENTITY_SEARCH_QUERY_MAX_LEN
    ? raw.slice(0, ENTITY_SEARCH_QUERY_MAX_LEN)
    : raw;
}

export async function fetchEntitySearch(
  query: string,
): Promise<EntitySearchResponse> {
  return getEntitySearchAPI(query);
}

function escapeBold(s: string): string {
  return s.replace(/\*\*/g, "''");
}

/** Turn API JSON into a short markdown-style string for the assistant panel. */
export function formatEntitySearchResults(data: EntitySearchResponse): string {
  const { query, results } = data;
  const { tags, tasks, projects } = results;
  const total = tags.length + tasks.length + projects.length;

  if (total === 0) {
    return `**No matches** for “${escapeBold(query)}” in your tasks, tags, or project names/descriptions. Try another keyword (min. 2 characters).`;
  }

  const lines: string[] = [`**Workspace search:** “${escapeBold(query)}”`, ""];

  if (tasks.length) {
    lines.push(`**Tasks** (${tasks.length})`);
    for (const t of tasks.slice(0, 8)) {
      const tag = t.tagName ? ` · ${t.tagName}` : "";
      lines.push(`• **${escapeBold(t.title)}** (${t.status}${tag})`);
      if (t.snippet?.trim()) {
        lines.push(`  ${escapeBold(t.snippet.trim())}`);
      }
    }
    lines.push("");
  }

  if (tags.length) {
    lines.push(`**Tags** (${tags.length})`);
    for (const g of tags.slice(0, 8)) {
      lines.push(`• **${escapeBold(g.name)}**`);
    }
    lines.push("");
  }

  if (projects.length) {
    lines.push(`**Projects** (${projects.length})`);
    for (const p of projects.slice(0, 8)) {
      lines.push(`• **${escapeBold(p.name)}**`);
      if (p.description?.trim()) {
        lines.push(`  ${escapeBold(p.description.trim())}`);
      }
    }
  }

  return lines.join("\n").trimEnd();
}
