/**
 * Thin API client for the FastAPI backend.
 *
 * All network calls live in this one file, so components never call
 * fetch() directly. This keeps error handling (network vs. HTTP vs.
 * validation errors) consistent everywhere, and means the base URL only
 * needs to be configured in one place.
 *
 * NOTE on security: this file never touches any AI provider API key - it
 * only ever talks to OUR backend, which is the only thing that holds the
 * key. See backend/.env / README "Security Considerations".
 */
import type { AnalyzeResponse, Category, Priority, SavedRequest } from "../types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

/** A user-safe error raised by the API client. `message` is always fit to
 * show directly in the UI - never a raw stack trace or internal detail. */
export class ApiError extends Error {
  status?: number;

  constructor(message: string, status?: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  let response: Response;

  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
  } catch {
    // fetch() throws (not a rejected HTTP status) when the network is down
    // or the backend simply isn't running.
    throw new ApiError(
      "Could not reach the server. Please make sure the backend is running and try again."
    );
  }

  if (!response.ok) {
    let detail = `Request failed (status ${response.status}).`;
    try {
      const body = await response.json();
      if (typeof body?.detail === "string") {
        detail = body.detail;
      } else if (Array.isArray(body?.detail)) {
        // FastAPI/Pydantic validation errors come back as a list of
        // { loc, msg, type } objects - surface the first message.
        detail = body.detail[0]?.msg ?? detail;
      }
    } catch {
      // Response body wasn't JSON - fall back to the generic message above.
    }
    throw new ApiError(detail, response.status);
  }

  // No content (e.g. some future 204 endpoint).
  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

export function analyzeDescription(description: string): Promise<AnalyzeResponse> {
  return request<AnalyzeResponse>("/api/analyze", {
    method: "POST",
    body: JSON.stringify({ description }),
  });
}

export function createRequest(payload: {
  problem: string;
  category: Category;
  priority: Priority;
}): Promise<SavedRequest> {
  return request<SavedRequest>("/api/requests", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getRequests(): Promise<SavedRequest[]> {
  return request<SavedRequest[]>("/api/requests", { method: "GET" });
}

export function checkHealth(): Promise<{ status: string; ai_provider: string }> {
  return request("/api/health", { method: "GET" });
}
