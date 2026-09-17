import { Navigate, Route, Routes } from "react-router-dom";
import { Navigation } from "./components/Navigation";
import { NewRequestPage } from "./pages/NewRequestPage";
import { RequestsPage } from "./pages/RequestsPage";

export default function App() {
  return (
    <div className="app-shell">
      <Navigation />
      <main className="app-main">
        <Routes>
          <Route path="/" element={<Navigate to="/new-request" replace />} />
          <Route path="/new-request" element={<NewRequestPage />} />
          <Route path="/requests" element={<RequestsPage />} />
          <Route path="*" element={<Navigate to="/new-request" replace />} />
        </Routes>
      </main>
    </div>
  );
}
