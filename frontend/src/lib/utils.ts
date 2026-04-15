import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/** Reads API error message from legacy `{ message }` or `{ error: { message } }` bodies. */
export function getApiErrorMessage(data: unknown): string {
  if (!data || typeof data !== "object") {
    return "Something went wrong";
  }
  const d = data as Record<string, unknown>;
  if (typeof d.message === "string" && d.message) {
    return d.message;
  }
  const err = d.error as Record<string, unknown> | undefined;
  if (err && typeof err.message === "string" && err.message) {
    return err.message;
  }
  return "Something went wrong";
}
