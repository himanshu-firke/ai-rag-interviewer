"use client";

import { useAuth } from "@/lib/auth-context";
import { useRouter } from "next/navigation";

export default function NavBar() {
  const { user, isLoggedIn, logout, loading } = useAuth();
  const router = useRouter();

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  return (
    <nav className="navbar">
      <div className="navbar-content">
        <a href="/" className="navbar-brand">
          <span className="navbar-brand-icon">AI</span>
          InterviewAI
        </a>
        <div className="navbar-links">
          <a href="/" className="navbar-link">Home</a>
          {isLoggedIn ? (
            <>
              <a href="/upload" className="navbar-link">New Interview</a>
              <a href="/history" className="navbar-link">History</a>
              <span style={{
                padding: "6px 14px", fontSize: "0.8rem", color: "var(--text-secondary)",
                display: "flex", alignItems: "center", gap: 8,
              }}>
                <span style={{
                  width: 24, height: 24, borderRadius: "50%",
                  background: "#000000", display: "flex",
                  alignItems: "center", justifyContent: "center",
                  fontSize: "0.65rem", fontWeight: 700, color: "white",
                }}>{user?.name?.[0]?.toUpperCase() || "U"}</span>
                {user?.name}
              </span>
              <button onClick={handleLogout} className="navbar-link"
                style={{ background: "none", border: "none", cursor: "pointer",
                  fontFamily: "var(--font-sans)", fontSize: "0.875rem", color: "var(--text-muted)" }}>
                Logout
              </button>
            </>
          ) : (
            <a href="/login" className="navbar-link">Login</a>
          )}
        </div>
      </div>
    </nav>
  );
}
