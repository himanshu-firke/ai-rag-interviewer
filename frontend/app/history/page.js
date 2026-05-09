"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/lib/auth-context";
import { getHistory } from "@/lib/api";

export default function HistoryPage() {
  const router = useRouter();
  const { isLoggedIn, loading: authLoading, user } = useAuth();
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!authLoading && !isLoggedIn) { router.push("/login"); return; }
    if (!authLoading && isLoggedIn) {
      async function fetch() {
        try {
          const data = await getHistory();
          setSessions(data.sessions || []);
        } catch (err) { setError(err.message); }
        finally { setLoading(false); }
      }
      fetch();
    }
  }, [authLoading, isLoggedIn, router]);

  const getRecColor = (rec) => {
    return { strong_hire: "#10b981", hire: "#06b6d4", maybe: "#f59e0b", no_hire: "#ef4444" }[rec] || "#64748b";
  };

  const getStatusStyle = (status) => {
    if (status === "completed") return { bg: "rgba(16, 185, 129, 0.1)", color: "#10b981" };
    if (status === "in_progress") return { bg: "rgba(99, 102, 241, 0.1)", color: "#6366f1" };
    return { bg: "rgba(100, 116, 139, 0.1)", color: "#64748b" };
  };

  const formatDate = (iso) => {
    if (!iso) return "—";
    // Ensure the date is parsed as UTC by appending 'Z' if missing
    const utcStr = iso.endsWith("Z") ? iso : `${iso}Z`;
    return new Date(utcStr).toLocaleString("en-US", { 
      month: "short", day: "numeric", year: "numeric", 
      hour: "2-digit", minute: "2-digit" 
    });
  };

  if (authLoading || loading) {
    return (
      <div className="page"><div className="container" style={{ maxWidth: 1000, textAlign: "center", paddingTop: 80 }}>
        <div className="skeleton" style={{ width: 300, height: 30, margin: "0 auto 20px" }} />
        {[1,2,3].map(i => <div key={i} className="skeleton mb-4" style={{ height: 80, borderRadius: 12 }} />)}
      </div></div>
    );
  }

  return (
    <div className="page">
      <div className="container" style={{ maxWidth: 1000 }}>
        <div className="flex justify-between items-center mb-6 animate-fade-in">
          <div>
            <h1 style={{ fontSize: "1.8rem", marginBottom: 4 }}>My Interview History</h1>
            <p className="text-secondary">{sessions.length} session{sessions.length !== 1 ? "s" : ""} • {user?.name}</p>
          </div>
          <Link href="/upload" className="btn btn-primary">+ New Interview</Link>
        </div>

        {error && (
          <div className="glass-card mb-4" style={{ borderColor: "rgba(239, 68, 68, 0.3)" }}>
            <p style={{ color: "var(--accent-danger)" }}>{error}</p>
          </div>
        )}

        {sessions.length === 0 ? (
          <div className="glass-card" style={{ textAlign: "center", padding: "60px 32px" }}>
            <p style={{ fontSize: "2.5rem", marginBottom: 16 }}>📋</p>
            <h3 style={{ marginBottom: 8 }}>No interviews yet</h3>
            <p className="text-secondary mb-4">Start your first AI-powered interview.</p>
            <Link href="/upload" className="btn btn-primary">Start Interview</Link>
          </div>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            {sessions.map((s, i) => {
              const st = getStatusStyle(s.status);
              const rc = getRecColor(s.recommendation);
              return (
                <div key={s.session_id} className="glass-card animate-slide-up"
                  style={{ padding: "20px 24px", animationDelay: `${i * 50}ms` }}>
                  <div className="flex justify-between items-center" style={{ flexWrap: "wrap", gap: 12 }}>
                    <div style={{ flex: 1, minWidth: 200 }}>
                      <div className="flex items-center gap-2 mb-1">
                        <h3 style={{ fontSize: "1.05rem", margin: 0 }}>{s.role}</h3>
                        <span style={{
                          padding: "2px 10px", borderRadius: 20, fontSize: "0.65rem", fontWeight: 600,
                          textTransform: "uppercase", background: st.bg, color: st.color,
                        }}>{s.status.replace("_", " ")}</span>
                      </div>
                      <div className="flex items-center gap-3" style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>
                        <span>{s.answered_questions}/{s.total_questions} questions</span>
                        <span>•</span>
                        <span>{formatDate(s.created_at)}</span>
                      </div>
                    </div>
                    <div style={{ textAlign: "center", minWidth: 80 }}>
                      {s.average_score !== null ? (
                        <>
                          <div style={{ fontSize: "1.6rem", fontWeight: 800, color: rc, lineHeight: 1 }}>{s.average_score}</div>
                          <div style={{ fontSize: "0.65rem", color: "var(--text-muted)" }}>/10</div>
                        </>
                      ) : <span className="text-muted" style={{ fontSize: "0.8rem" }}>—</span>}
                    </div>
                    <div className="flex items-center gap-3">
                      {s.recommendation && (
                        <span style={{
                          padding: "4px 14px", borderRadius: 20, fontSize: "0.7rem", fontWeight: 700,
                          textTransform: "uppercase", background: rc + "18", color: rc,
                        }}>{s.recommendation.replace("_", " ")}</span>
                      )}
                      {s.status === "completed" ? (
                        <Link href={`/results?session=${s.session_id}`} className="btn btn-secondary"
                          style={{ padding: "6px 16px", fontSize: "0.8rem" }}>View Results</Link>
                      ) : s.status === "in_progress" ? (
                        <Link href={`/interview?session=${s.session_id}`} className="btn btn-primary"
                          style={{ padding: "6px 16px", fontSize: "0.8rem" }}>Continue</Link>
                      ) : null}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
