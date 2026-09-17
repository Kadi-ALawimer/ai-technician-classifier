import { useEffect, useState } from "react";
import { CATEGORY_LABELS, PRIORITY_LABELS } from "../types";
import type { SavedRequest } from "../types";
import { ApiError, getRequests } from "../services/api";
import { LoadingSpinner } from "../components/LoadingSpinner";

function formatDate(isoString: string): string {
  try {
    return new Date(isoString).toLocaleString(undefined, {
      dateStyle: "medium",
      timeStyle: "short",
    });
  } catch {
    return isoString;
  }
}

export function RequestsPage() {
  const [requests, setRequests] = useState<SavedRequest[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;

    async function load() {
      setIsLoading(true);
      setError(null);
      try {
        const data = await getRequests();
        if (isMounted) setRequests(data);
      } catch (err) {
        if (isMounted) {
          setError(err instanceof ApiError ? err.message : "Failed to load requests. Please try again.");
        }
      } finally {
        if (isMounted) setIsLoading(false);
      }
    }

    load();
    return () => {
      isMounted = false;
    };
  }, []);

  return (
    <div>
      <div className="page-header">
        <p className="eyebrow">Saved Records</p>
        <h1>Requests</h1>
        <p>All saved technician requests.</p>
      </div>

      {isLoading && (
        <div className="loading-state">
          <LoadingSpinner variant="dark" />
          <p style={{ marginTop: "var(--space-2)" }}>Loading requests...</p>
        </div>
      )}

      {!isLoading && error && (
        <div className="alert alert-error" role="alert">
          {error}
        </div>
      )}

      {!isLoading && !error && requests && requests.length === 0 && (
        <div className="empty-state">
          <div className="empty-state-icon">🗂️</div>
          <p>No requests yet. Create one from the "New Request" page.</p>
        </div>
      )}

      {!isLoading && !error && requests && requests.length > 0 && (
        <>
          {/* Desktop / tablet: table layout */}
          <div className="request-table-wrapper">
            <table className="request-table">
              <thead>
                <tr>
                  <th>Problem</th>
                  <th>Category</th>
                  <th>Priority</th>
                  <th>Date</th>
                </tr>
              </thead>
              <tbody>
                {requests.map((req) => (
                  <tr key={req.id}>
                    <td dir="auto">{req.problem}</td>
                    <td>
                      <span className="badge category">{CATEGORY_LABELS[req.category]}</span>
                    </td>
                    <td>
                      <span className={`badge ${req.priority}`}>{PRIORITY_LABELS[req.priority]}</span>
                    </td>
                    <td>{formatDate(req.created_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Mobile: card layout (no cramped table on small screens) */}
          <div className="request-cards-mobile request-list">
            {requests.map((req) => (
              <div className="card" key={req.id}>
                <p className="card-problem-text" dir="auto" style={{ marginBottom: "var(--space-2)" }}>
                  {req.problem}
                </p>
                <div className="request-meta-row">
                  <span className="badge category">{CATEGORY_LABELS[req.category]}</span>
                  <span className={`badge ${req.priority}`}>{PRIORITY_LABELS[req.priority]}</span>
                  <span className="request-date">{formatDate(req.created_at)}</span>
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}