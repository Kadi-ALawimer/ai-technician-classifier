interface LoadingSpinnerProps {
  variant?: "light" | "dark";
}

/** Small inline spinner reused for both button-loading and page-loading states. */
export function LoadingSpinner({ variant = "light" }: LoadingSpinnerProps) {
  return <span className={`spinner${variant === "dark" ? " spinner-dark" : ""}`} aria-hidden="true" />;
}
