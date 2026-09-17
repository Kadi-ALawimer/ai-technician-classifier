import { useState } from "react";
import type { FormEvent } from "react";
import { ProblemResultCard } from "../components/ProblemResultCard";
import { LoadingSpinner } from "../components/LoadingSpinner";
import { analyzeDescription, ApiError, createRequest } from "../services/api";
import type { Category, EditableProblem, Priority } from "../types";

const MIN_DESCRIPTION_LENGTH = 3;

function toEditableProblems(requests: { problem: string; category: Category; priority: Priority }[]): EditableProblem[] {
  return requests.map((req, index) => ({
    ...req,
    localId: `${Date.now()}-${index}-${Math.random().toString(36).slice(2, 8)}`,
    saveState: "idle",
  }));
}

export function NewRequestPage() {
  const [description, setDescription] = useState("");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analyzeError, setAnalyzeError] = useState<string | null>(null);
  const [results, setResults] = useState<EditableProblem[] | null>(null);

  const trimmedLength = description.trim().length;
  const canSubmit = trimmedLength >= MIN_DESCRIPTION_LENGTH && !isAnalyzing;

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (!canSubmit) {
      if (trimmedLength === 0) {
        setAnalyzeError("Please describe your problem before analyzing.");
      }
      return;
    }

    setIsAnalyzing(true);
    setAnalyzeError(null);
    setResults(null);

    try {
      const response = await analyzeDescription(description.trim());
      setResults(toEditableProblems(response.requests));
    } catch (error) {
      const message = error instanceof ApiError ? error.message : "Something went wrong. Please try again.";
      setAnalyzeError(message);
    } finally {
      setIsAnalyzing(false);
    }
  }

  function updateCategory(localId: string, category: Category) {
    setResults((prev) =>
      prev ? prev.map((item) => (item.localId === localId ? { ...item, category } : item)) : prev
    );
  }

  function updatePriority(localId: string, priority: Priority) {
    setResults((prev) =>
      prev ? prev.map((item) => (item.localId === localId ? { ...item, priority } : item)) : prev
    );
  }

  async function handleConfirm(localId: string) {
    const target = results?.find((item) => item.localId === localId);
    if (!target) return;

    setResults((prev) =>
      prev
        ? prev.map((item) =>
            item.localId === localId ? { ...item, saveState: "saving", saveError: undefined } : item
          )
        : prev
    );

    try {
      await createRequest({
        problem: target.problem,
        category: target.category,
        priority: target.priority,
      });
      setResults((prev) =>
        prev ? prev.map((item) => (item.localId === localId ? { ...item, saveState: "saved" } : item)) : prev
      );
    } catch (error) {
      const message = error instanceof ApiError ? error.message : "Failed to save this request. Please try again.";
      setResults((prev) =>
        prev
          ? prev.map((item) =>
              item.localId === localId ? { ...item, saveState: "error", saveError: message } : item
            )
          : prev
      );
    }
  }

  function handleReset() {
    setDescription("");
    setResults(null);
    setAnalyzeError(null);
  }

  return (
    <div>
      <div className="page-header">
        <p className="eyebrow">Classification Engine</p>
        <h1>New Request</h1>
        <p>Describe your problem in your own words - in Arabic or English - and let AI classify it.</p>
      </div>

      <form className="card" onSubmit={handleSubmit}>
        <div className="field-group" style={{ marginBottom: "var(--space-3)" }}>
          <label className="field-label" htmlFor="description">
            Problem description
          </label>
          <textarea
            id="description"
            dir="auto"
            placeholder="Describe your problem, for example: My kitchen sink is leaking..."
            value={description}
            disabled={isAnalyzing}
            onChange={(event) => setDescription(event.target.value)}
            maxLength={2000}
          />
        </div>

        {analyzeError && (
          <div className="alert alert-error" role="alert">
            {analyzeError}
          </div>
        )}

        <button type="submit" className="btn btn-primary" disabled={!canSubmit}>
          {isAnalyzing && <LoadingSpinner />}
          {isAnalyzing ? "Analyzing..." : "Analyze"}
        </button>
      </form>

      {results && results.length > 0 && (
        <div style={{ marginTop: "var(--space-5)" }}>
          <div className="detected-banner">
            Detected {results.length} request{results.length > 1 ? "s" : ""}
          </div>

          {results.map((item, index) => (
            <ProblemResultCard
              key={item.localId}
              index={index}
              item={item}
              onCategoryChange={updateCategory}
              onPriorityChange={updatePriority}
              onConfirm={handleConfirm}
            />
          ))}

          <button
            type="button"
            className="btn btn-secondary"
            style={{ marginTop: "var(--space-4)", width: "100%" }}
            onClick={handleReset}
          >
            Start a new description
          </button>
        </div>
      )}
    </div>
  );
}