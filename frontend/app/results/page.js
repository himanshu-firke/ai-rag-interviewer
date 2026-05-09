"use client";

import { useState, useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { getReport, exportReport, getPdfReportUrl } from "@/lib/api";

function ResultsContent() {
  const searchParams = useSearchParams();
  const sessionId = searchParams.get("session");

  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!sessionId) return;
    async function fetchReport() {
      try { setReport(await getReport(sessionId)); }
      catch (err) { setError(err.message); }
      finally { setLoading(false); }
    }
    fetchReport();
  }, [sessionId]);

  const handleJsonExport = async () => {
    try {
      const data = await exportReport(sessionId);
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a"); a.href = url;
      a.download = `Interview_Report_${sessionId}.json`; a.click();
      URL.revokeObjectURL(url);
    } catch (err) { alert("Export failed: " + err.message); }
  };

  if (loading) {
    return (
      <div className="page">
        <div className="container" style={{ maxWidth: 850, textAlign: "center", paddingTop: 80 }}>
          <div className="skeleton" style={{ width: 60, height: 60, borderRadius: "50%", margin: "0 auto 20px" }} />
          <div className="skeleton" style={{ width: 350, height: 24, margin: "0 auto 12px" }} />
          <p className="text-muted mt-4">Generating your report...</p>
        </div>
      </div>
    );
  }

  if (error || !report) {
    return (
      <div className="page">
        <div className="container" style={{ maxWidth: 600, textAlign: "center", paddingTop: 80 }}>
          <div className="glass-card">
            <h2>Error</h2>
            <p className="text-muted">{error || "Report not found"}</p>
            <a href="/upload" className="btn btn-primary mt-4">Start New Interview</a>
          </div>
        </div>
      </div>
    );
  }

  const { report: rpt, questions, candidate, role } = report;
  const score = rpt?.overall_score || 0;
  const rec = (rpt?.recommendation || "maybe").replace("_", " ").toUpperCase();
  const c = score >= 8 ? "#10b981" : score >= 6.5 ? "#06b6d4" : score >= 4.5 ? "#f59e0b" : "#ef4444";

  return (
    <div className="page">
      <div className="container" style={{ maxWidth: 900 }}>
        {/* Score Header */}
        <div className="glass-card mb-4 animate-fade-in" style={{ textAlign: "center", padding: "32px 24px" }}>
          <div style={{
            width: 120, height: 120, borderRadius: "50%", margin: "0 auto 16px",
            background: `conic-gradient(${c} ${score * 10}%, rgba(255,255,255,0.05) 0%)`,
            display: "flex", alignItems: "center", justifyContent: "center",
          }}>
            <div style={{
              width: 96, height: 96, borderRadius: "50%", background: "var(--bg-card)",
              display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center",
            }}>
              <span style={{ fontSize: "2rem", fontWeight: 800, color: c }}>{score}</span>
              <span style={{ fontSize: "0.7rem", color: "var(--text-muted)" }}>/10</span>
            </div>
          </div>
          <h1 style={{ fontSize: "1.5rem", marginBottom: 4 }}>Interview Results</h1>
          <p className="text-secondary" style={{ marginBottom: 8 }}>{candidate?.name} — {role}</p>
          <span style={{
            display: "inline-block", padding: "6px 20px", borderRadius: 20,
            background: c + "22", color: c, fontWeight: 700, fontSize: "0.85rem",
          }}>{rec}</span>

          <div className="flex gap-3 mt-5" style={{ justifyContent: "center" }}>
            <button className="btn btn-primary" onClick={() => window.open(getPdfReportUrl(sessionId), "_blank")}
              style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                <polyline points="14 2 14 8 20 8" /><line x1="12" y1="18" x2="12" y2="12" />
                <polyline points="9 15 12 18 15 15" />
              </svg>Download PDF
            </button>
            <button className="btn btn-secondary" onClick={handleJsonExport}
              style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polyline points="16 18 22 12 16 6" /><polyline points="8 6 2 12 8 18" />
              </svg>Export JSON
            </button>
          </div>
        </div>

        {/* Summary */}
        {rpt?.summary && (
          <div className="glass-card mb-4 animate-slide-up">
            <h3 style={{ marginBottom: 10, fontSize: "1.1rem" }}>Summary</h3>
            <p className="text-secondary" style={{ lineHeight: 1.7 }}>{rpt.summary}</p>
          </div>
        )}

        {/* Strengths & Weaknesses */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }} className="mb-4">
          <div className="glass-card animate-slide-up">
            <h3 style={{ color: "#10b981", marginBottom: 12, fontSize: "1rem" }}>Strengths</h3>
            {(rpt?.strengths || []).map((s, i) => (
              <div key={i} className="flex items-center gap-2 mb-2">
                <span style={{ color: "#10b981" }}>✓</span>
                <span className="text-secondary" style={{ fontSize: "0.9rem" }}>{s}</span>
              </div>
            ))}
          </div>
          <div className="glass-card animate-slide-up">
            <h3 style={{ color: "#f59e0b", marginBottom: 12, fontSize: "1rem" }}>Areas to Improve</h3>
            {(rpt?.weaknesses || []).map((w, i) => (
              <div key={i} className="flex items-center gap-2 mb-2">
                <span style={{ color: "#f59e0b" }}>△</span>
                <span className="text-secondary" style={{ fontSize: "0.9rem" }}>{w}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Question Breakdown */}
        <div className="glass-card mb-4 animate-slide-up">
          <h3 style={{ marginBottom: 16, fontSize: "1.1rem" }}>Question Breakdown</h3>
          {(questions || []).map((q, i) => {
            const qs = q.scores || {};
            const s = qs.overall || 0;
            const sc = s >= 8 ? "#10b981" : s >= 6 ? "#06b6d4" : s >= 4 ? "#f59e0b" : "#ef4444";
            const isCoding = (q.question_type || q.type) === "coding";

            return (
              <div key={i} style={{
                padding: 16, marginBottom: 12, borderRadius: "var(--radius-sm)",
                background: "rgba(255,255,255,0.02)", border: "1px solid var(--border-default)",
              }}>
                <div className="flex items-center gap-2 mb-2">
                  <span style={{
                    width: 28, height: 28, borderRadius: "50%", background: sc + "22", color: sc,
                    display: "flex", alignItems: "center", justifyContent: "center",
                    fontSize: "0.75rem", fontWeight: 700,
                  }}>{q.number}</span>
                  <span className="tag tag-info" style={{ fontSize: "0.6rem" }}>{q.topic}</span>
                  <span className="tag tag-warning" style={{ fontSize: "0.6rem" }}>{q.difficulty}</span>
                  {isCoding && <span className="tag tag-primary" style={{ fontSize: "0.6rem" }}>CODE</span>}
                  <span style={{ marginLeft: "auto", fontWeight: 700, color: sc, fontSize: "0.9rem" }}>{s}/10</span>
                </div>

                <p style={{ fontWeight: 500, marginBottom: 8, fontSize: "0.9rem" }}>{q.question}</p>

                {/* Answer */}
                <div style={{
                  padding: "10px 14px", borderRadius: "var(--radius-xs)", marginBottom: 8,
                  background: isCoding ? "#0d1117" : "rgba(99, 102, 241, 0.05)",
                  borderLeft: isCoding ? "3px solid #6366f1" : "3px solid rgba(99, 102, 241, 0.3)",
                }}>
                  <pre style={{
                    fontSize: "0.83rem", lineHeight: 1.6, whiteSpace: "pre-wrap", margin: 0,
                    fontFamily: isCoding ? "var(--font-mono)" : "var(--font-sans)",
                    color: isCoding ? "#c9d1d9" : "var(--text-secondary)",
                  }}>{q.answer || "Not answered"}</pre>
                </div>

                {/* Scores */}
                <div className="flex gap-4 mb-2" style={{ fontSize: "0.75rem", flexWrap: "wrap" }}>
                  {isCoding ? (
                    <>
                      <span className="text-muted">Correctness: <strong style={{ color: sc }}>{qs.correctness || 0}</strong></span>
                      <span className="text-muted">Optimization: <strong style={{ color: sc }}>{qs.clarity || 0}</strong></span>
                      <span className="text-muted">Code Quality: <strong style={{ color: sc }}>{qs.depth || 0}</strong></span>
                      <span className="text-muted">Originality: <strong style={{ color: s >= 6 ? "#10b981" : "#f59e0b" }}>
                        {qs.correctness ? "✓" : "—"}
                      </strong></span>
                    </>
                  ) : (
                    <>
                      <span className="text-muted">Correctness: <strong style={{ color: sc }}>{qs.correctness || 0}</strong></span>
                      <span className="text-muted">Depth: <strong style={{ color: sc }}>{qs.depth || 0}</strong></span>
                      <span className="text-muted">Clarity: <strong style={{ color: sc }}>{qs.clarity || 0}</strong></span>
                    </>
                  )}
                </div>

                {q.feedback && (
                  <p style={{ fontSize: "0.8rem", color: "var(--text-muted)", fontStyle: "italic" }}>{q.feedback}</p>
                )}
              </div>
            );
          })}
        </div>

        <div style={{ textAlign: "center", marginBottom: 40 }} className="flex gap-3" style={{ justifyContent: "center", marginBottom: 40 }}>
          <a href="/history" className="btn btn-secondary">View History</a>
          <a href="/upload" className="btn btn-primary">New Interview</a>
        </div>
      </div>
    </div>
  );
}

export default function ResultsPage() {
  return (
    <Suspense fallback={<div className="page"><div className="container" style={{ maxWidth: 850, textAlign: "center", paddingTop: 80 }}><p className="text-muted">Loading results...</p></div></div>}>
      <ResultsContent />
    </Suspense>
  );
}
