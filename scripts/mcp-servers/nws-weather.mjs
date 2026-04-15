/**
 * NWS weather MCP: api.weather.gov (GeoJSON). Tools: get_forecast, get_alerts.
 */
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import * as z from "zod";

const NWS = "https://api.weather.gov";
const HEADERS = {
  "User-Agent": "todo-app-flask-reactjs/mcp-servers/nws-weather (https://github.com/)",
  Accept: "application/geo+json, application/ld+json, application/json",
};

async function readNwsJson(url) {
  const res = await fetch(url, { headers: HEADERS });
  const text = await res.text();
  if (!res.ok) {
    throw new Error(`NWS HTTP ${res.status}: ${text.slice(0, 300)}`);
  }
  return JSON.parse(text);
}

function formatAlert(feature) {
  const p = feature.properties ?? {};
  return [
    `Event: ${p.event ?? "?"}`,
    `Area: ${p.areaDesc ?? "?"}`,
    `Severity: ${p.severity ?? "?"}`,
    `Headline: ${p.headline ?? "?"}`,
    "---",
  ].join("\n");
}

const mcp = new McpServer({ name: "nws-weather", version: "1.0.0" });

mcp.registerTool(
  "get_forecast",
  {
    description: "Get NWS weather forecast for a US location (latitude, longitude).",
    inputSchema: {
      latitude: z.number().min(-90).max(90),
      longitude: z.number().min(-180).max(180),
    },
  },
  async ({ latitude, longitude }) => {
    const pts = `${latitude},${longitude}`;
    const points = await readNwsJson(`${NWS}/points/${pts}`);
    const forecastUrl = points.properties?.forecast;
    if (!forecastUrl) {
      return {
        content: [{ type: "text", text: "No forecast URL in NWS grid metadata." }],
        isError: true,
      };
    }
    const forecast = await readNwsJson(forecastUrl);
    const periods = forecast.properties?.periods ?? [];
    if (!periods.length) {
      return {
        content: [{ type: "text", text: "No forecast periods in NWS response." }],
        isError: true,
      };
    }
    const lines = periods.slice(0, 14).map(
      (p) =>
        `${p.name}: ${p.temperature ?? "?"}°${p.temperatureUnit ?? ""} — ${p.shortForecast ?? ""} (wind ${p.windSpeed ?? "?"})`,
    );
    return {
      content: [{ type: "text", text: `Forecast for ${pts}:\n\n${lines.join("\n")}` }],
    };
  },
);

mcp.registerTool(
  "get_alerts",
  {
    description: "Get active NWS weather alerts for a US state (two-letter code).",
    inputSchema: { state: z.string().length(2) },
  },
  async ({ state }) => {
    const code = state.toUpperCase();
    const data = await readNwsJson(`${NWS}/alerts?area=${code}&status=actual`);
    const features = data.features ?? [];
    if (!features.length) {
      return { content: [{ type: "text", text: `No active alerts for ${code}.` }] };
    }
    return {
      content: [
        {
          type: "text",
          text: `Active alerts for ${code}:\n\n${features.map(formatAlert).join("\n")}`,
        },
      ],
    };
  },
);

const transport = new StdioServerTransport();
await mcp.connect(transport);
