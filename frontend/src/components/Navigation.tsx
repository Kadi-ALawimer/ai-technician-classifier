import { NavLink } from "react-router-dom";
import { BrandMark } from "./BrandMark";

/**
 * Top navigation bar. Sticky, mobile-first, and only two links - the spec
 * intentionally keeps this project to two pages (no auth, no admin, no
 * extra sections), so the nav stays simple on purpose.
 *
 * "Fixora AI" is a product-identity / visual-design change only: routes,
 * data, and API calls are untouched.
 */
export function Navigation() {
  return (
    <header className="nav-bar">
      <div className="nav-bar-inner">
        <NavLink to="/new-request" className="nav-brand">
          <span className="nav-brand-mark">
            <BrandMark />
          </span>
          <span className="nav-brand-text">
            <span className="nav-brand-name">Fixora AI</span>
            <span className="nav-brand-tagline">Smart Technician Request Classification</span>
          </span>
        </NavLink>
        <nav className="nav-links">
          <NavLink
            to="/new-request"
            className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}
          >
            New Request
          </NavLink>
          <NavLink
            to="/requests"
            className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}
          >
            Requests
          </NavLink>
        </nav>
      </div>
    </header>
  );
}