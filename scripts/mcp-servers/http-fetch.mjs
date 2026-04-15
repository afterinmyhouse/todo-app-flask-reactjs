/**
 * HTTP fetch MCP: read public HTML/JSON/text for agent context (docs, tables, APIs).
 * GET only, https/http, response truncated for safety.
 */
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import * as z from "zod";

const DEFAULT_MAX = 120_000;
const UA = "todo-app-flask-reactjs/mcp-servers/http-fetch (https://github.com/)";

function safeUrl(raw) {
  let u;
  try {
    u = new URL(raw);
  } catch {
    return null;
  }
  if (u.protocol !== "http:" && u.protocol !== "https:") return null;
  return u;
}

const mcp = new McpServer({ name: "http-fetch", version: "1.0.0" });

mcp.registerTool(
  "fetch_url",
  {
    description:
      "HTTP GET a public URL and return the response body as text (truncated). Use for HTML pages, JSON APIs, or plain text. Only http(s).",
    inputSchema: {
      url: z.string().describe("Absolute http(s) URL"),
      maxChars: z
        .number()
        .int()
        .min(1_000)
        .max(DEFAULT_MAX)
        .optional()
        .describe(`Max characters of body (default ${DEFAULT_MAX})`),
    },
  },
  async ({ url, maxChars }) => {
    const u = safeUrl(url);
    if (!u) {
      return {
        content: [{ type: "text", text: "Invalid URL: only http and https are allowed." }],
        isError: true,
      };
    }
    const cap = maxChars ?? DEFAULT_MAX;
    const res = await fetch(u, {
      method: "GET",
      redirect: "follow",
      headers: {
        "User-Agent": UA,
        Accept: "*/*",
      },
    });
    const ct = res.headers.get("content-type") ?? "";
    const text = await res.text();
    const truncated = text.length > cap;
    const body = truncated ? text.slice(0, cap) + "\n\n[…truncated…]" : text;
    const head = `URL: ${u.href}\nHTTP ${res.status}\nContent-Type: ${ct}\nLength: ${text.length} chars\n\n`;
    return {
      content: [{ type: "text", text: head + body }],
      isError: !res.ok,
    };
  },
);

const transport = new StdioServerTransport();
await mcp.connect(transport);
