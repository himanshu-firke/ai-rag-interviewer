"use client";

import { useState, useRef, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { createSession } from "@/lib/api";

export default function UploadPage() {
  const router = useRouter();
  const { user, isLoggedIn, loading: authLoading } = useAuth();
  const fileInputRef = useRef(null);

  const [role, setRole] = useState("");
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");
  const [dragOver, setDragOver] = useState(false);

  useEffect(() => {
    if (!authLoading && !isLoggedIn) router.push("/login");
  }, [authLoading, isLoggedIn, router]);

  if (authLoading || !isLoggedIn) {
    return (
      <div className="page"><div className="container" style={{ maxWidth: 600, textAlign: "center", paddingTop: 100 }}>
        <p className="text-muted">Checking authentication...</p>
      </div></div>
    );
  }

  const handleFile = (f) => {
    if (f && f.type === "application/pdf") { setFile(f); setError(""); }
    else setError("Please upload a PDF file");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file || !role) { setError("Please select a role and upload your resume"); return; }
    setUploading(true); setError("");
    try {
      const result = await createSession(role, file);
      // Go directly to interview — no compatibility step
      router.push(`/interview?session=${result.session_id}`);
    } catch (err) { setError(err.message); setUploading(false); }
  };

  return (
    <div className="page">
      <div className="container" style={{ maxWidth: 560 }}>
        <div className="glass-card animate-fade-in" style={{ padding: "40px 36px" }}>
          <div style={{ textAlign: "center", marginBottom: 28 }}>
            <h2 style={{ fontSize: "1.5rem", marginBottom: 8 }}>Start Interview</h2>
            <p className="text-secondary" style={{ fontSize: "0.9rem" }}>
              Welcome, <strong>{user?.name}</strong> ({user?.email})
            </p>
          </div>

          <form onSubmit={handleSubmit}>
            {/* Role Selection */}
            <div className="form-group">
              <label className="form-label" style={{ fontWeight: 600, color: "#0b0f19" }}>Select Role</label>
              <select className="form-select" value={role} onChange={e => setRole(e.target.value)} required
                style={{ padding: "14px 16px", borderRadius: "8px", backgroundColor: "#f9fafb" }}>
                <option value="">Choose a role...</option>
                <option value="AI/ML Engineer">AI/ML Engineer</option>
                <option value="Backend Engineer">Backend Engineer</option>
                <option value="Data Scientist">Data Scientist</option>
                <option value="Full Stack Engineer">Full Stack Engineer</option>
              </select>
            </div>

            {/* Upload Zone */}
            <div className="form-group">
              <label className="form-label" style={{ fontWeight: 600, color: "#0b0f19" }}>Upload Resume (PDF)</label>
              <div className={`upload-zone ${dragOver ? "drag-over" : ""} ${file ? "has-file" : ""}`}
                onClick={() => fileInputRef.current?.click()}
                onDragOver={e => { e.preventDefault(); setDragOver(true); }}
                onDragLeave={() => setDragOver(false)}
                onDrop={e => { e.preventDefault(); setDragOver(false); handleFile(e.dataTransfer.files[0]); }}>
                <input ref={fileInputRef} type="file" accept=".pdf" hidden
                  onChange={e => handleFile(e.target.files[0])} />
                {file ? (
                  <>
                    <p className="upload-icon">✓</p>
                    <p className="upload-text" style={{ color: "var(--accent-success)" }}>{file.name}</p>
                    <p className="upload-hint">{(file.size / 1024).toFixed(0)} KB — Click to change</p>
                  </>
                ) : (
                  <>
                    <p className="upload-icon">📄</p>
                    <p className="upload-text">Drop your resume here or click to browse</p>
                    <p className="upload-hint">PDF files only</p>
                  </>
                )}
              </div>
            </div>

            {error && (
              <div style={{ padding: "12px 16px", borderRadius: "8px",
                background: "rgba(239, 68, 68, 0.08)", color: "#ef4444",
                border: "1px solid rgba(239, 68, 68, 0.2)",
                marginBottom: 16, fontSize: "0.9rem" }}>{error}</div>
            )}

            <button className="btn btn-primary w-full" type="submit" disabled={uploading || !file || !role}
              style={{ width: "100%", padding: "16px", fontSize: "1rem", borderRadius: "8px" }}>
              {uploading ? (
                <span style={{ display: "flex", alignItems: "center", gap: 10, justifyContent: "center" }}>
                  <span style={{ display: "inline-block", width: 18, height: 18, border: "2px solid rgba(255,255,255,0.3)", borderTopColor: "white", borderRadius: "50%", animation: "spin 0.6s linear infinite" }} />
                  Preparing Interview...
                </span>
              ) : "Upload & Start Interview →"}
            </button>
          </form>
        </div>
      </div>
      <style dangerouslySetInnerHTML={{__html: `@keyframes spin { to { transform: rotate(360deg); } }`}} />
    </div>
  );
}
