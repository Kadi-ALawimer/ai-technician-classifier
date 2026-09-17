import { CATEGORIES, CATEGORY_LABELS, PRIORITIES, PRIORITY_LABELS } from "../types";
import type { Category, EditableProblem, Priority } from "../types";
import { LoadingSpinner } from "./LoadingSpinner";

interface ProblemResultCardProps {
  index: number;
  item: EditableProblem;
  onCategoryChange: (localId: string, category: Category) => void;
  onPriorityChange: (localId: string, priority: Priority) => void;
  onConfirm: (localId: string) => void;
}

/**
 * One AI-classified problem, shown as an editable card. The user can
 * change the category/priority before saving - the backend is always the
 * final source of truth for validation (see README "Validation"), but
 * letting the user fix an obviously-wrong AI guess here is core UX.
 */
export function ProblemResultCard({
  index,
  item,
  onCategoryChange,
  onPriorityChange,
  onConfirm,
}: ProblemResultCardProps) {
  const isSaved = item.saveState === "saved";
  const isSaving = item.saveState === "saving";

  const reqTag = `REQ-${String(index + 1).padStart(2, "0")}`;

  return (
    <div className="card">
      <div className="card-title">{reqTag}</div>
      <p className="card-problem-text" dir="auto">
        {item.problem}
      </p>

      <div className="field-row">
        <div className="field-group">
          <label className="field-label" htmlFor={`category-${item.localId}`}>
            Category
          </label>
          <select
            id={`category-${item.localId}`}
            value={item.category}
            disabled={isSaved}
            onChange={(event) => onCategoryChange(item.localId, event.target.value as Category)}
          >
            {CATEGORIES.map((category) => (
              <option key={category} value={category}>
                {CATEGORY_LABELS[category]}
              </option>
            ))}
          </select>
        </div>

        <div className="field-group">
          <span className="field-label">Priority</span>
          <div className="priority-toggle" role="radiogroup" aria-label="Priority">
            {PRIORITIES.map((priority) => (
              <button
                type="button"
                key={priority}
                role="radio"
                aria-checked={item.priority === priority}
                disabled={isSaved}
                className={`priority-option${item.priority === priority ? ` selected ${priority}` : ""}`}
                onClick={() => onPriorityChange(item.localId, priority)}
              >
                {PRIORITY_LABELS[priority]}
              </button>
            ))}
          </div>
        </div>
      </div>

      {item.saveState === "error" && (
        <div className="alert alert-error" role="alert">
          {item.saveError ?? "Failed to save this request. Please try again."}
        </div>
      )}

      {isSaved ? (
        <div className="alert alert-success" role="status">
          Saved successfully.
        </div>
      ) : (
        <button
          type="button"
          className="btn btn-confirm"
          disabled={isSaving}
          onClick={() => onConfirm(item.localId)}
        >
          {isSaving && <LoadingSpinner />}
          {isSaving ? "Saving..." : "Confirm & Save"}
        </button>
      )}
    </div>
  );
}