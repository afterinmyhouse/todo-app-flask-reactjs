import axios from "axios";
import { useAuthStore } from "@/stores/auth-store";

/**
 * Shared API client.
 *
 * - Centralizes base URL (so we don't hardcode localhost across the app)
 * - Automatically attaches the JWT when available
 */
export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? "http://localhost:5000",
});

api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token;

  if (token) {
    config.headers = config.headers ?? {};
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

