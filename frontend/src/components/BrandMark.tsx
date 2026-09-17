interface BrandMarkProps {
  size?: number;
}

/**
 * Fixora AI logo mark — a small inline SVG combining a technical
 * "wrench + circuit node" motif to tie together the engineering
 * (technician requests) and AI (classification) sides of the product.
 * Uses currentColor so it inherits its color from CSS (.nav-brand-mark),
 * keeping it a pure presentational component with no external image asset.
 */
export function BrandMark({ size = 26 }: BrandMarkProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 32 32"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
      focusable="false"
    >
      <rect x="1" y="1" width="30" height="30" rx="6" stroke="currentColor" strokeWidth="1.5" opacity="0.35" />
      <path
        d="M20.5 7.5a4.5 4.5 0 0 0-5.86 5.86L8 20a2 2 0 1 0 2.83 2.83l6.64-6.64a4.5 4.5 0 0 0 5.86-5.86l-3 3-2.16-.72-.72-2.16 3-3Z"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinejoin="round"
        strokeLinecap="round"
      />
      <circle cx="23" cy="9" r="1.4" fill="currentColor" />
      <circle cx="9.2" cy="22.8" r="1" fill="currentColor" opacity="0.6" />
    </svg>
  );
}