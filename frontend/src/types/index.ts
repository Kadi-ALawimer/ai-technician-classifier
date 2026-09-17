/**
 * Shared TypeScript types.
 *
 * These mirror the backend's Pydantic schemas 1:1 (see
 * backend/app/schemas/request.py and backend/app/models/enums.py) so the
 * frontend and backend never silently drift apart on what values are
 * valid.
 */

export const CATEGORIES = [
  "plumbing",
  "electrical",
  "carpentry",
  "ac",
  "insulation",
  "flooring",
  "other",
] as const;

export type Category = (typeof CATEGORIES)[number];

export const PRIORITIES = ["normal", "urgent"] as const;

export type Priority = (typeof PRIORITIES)[number];

/** Human-readable labels for select inputs / badges. */
export const CATEGORY_LABELS: Record<Category, string> = {
  plumbing: "Plumbing",
  electrical: "Electrical",
  carpentry: "Carpentry",
  ac: "AC",
  insulation: "Insulation",
  flooring: "Flooring",
  other: "Other",
};

export const PRIORITY_LABELS: Record<Priority, string> = {
  normal: "Normal",
  urgent: "Urgent",
};

/** One problem as classified by the AI, before it has been saved. */
export interface ClassifiedProblem {
  problem: string;
  category: Category;
  priority: Priority;
}

/** Response shape of POST /api/analyze. */
export interface AnalyzeResponse {
  requests: ClassifiedProblem[];
}

/** A request as stored in (and returned from) the database. */
export interface SavedRequest {
  id: number;
  problem: string;
  category: Category;
  priority: Priority;
  created_at: string;
}

/** A classified problem being edited in the UI before it's saved, with a
 * stable local id so React can key/track each editable card. */
export interface EditableProblem extends ClassifiedProblem {
  localId: string;
  saveState: "idle" | "saving" | "saved" | "error";
  saveError?: string;
}
