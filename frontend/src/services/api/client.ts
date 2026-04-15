import axios from "axios";
import { useAuthStore } from "@/stores/auth-store";

/** Single source of truth for the backend origin (use in settings, links, etc.). */
export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:5000";

/**
 * Shared API client.
 *
 * - Centralizes base URL (so we don't hardcode localhost across the app)
 * - Automatically attaches the JWT when available
 */
export const api = axios.create({
  baseURL: API_BASE_URL,
});

api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token;

  if (token) {
    config.headers = config.headers ?? {};
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

