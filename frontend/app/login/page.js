"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { signup as apiSignup, login as apiLogin } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const { login, isLoggedIn } = useAuth();
  const [isSignup, setIsSignup] = useState(false);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  if (isLoggedIn) { router.push("/upload"); return null; }

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true); setError("");
    try {
      const data = isSignup
        ? await apiSignup(name.trim(), email.trim(), password)
        : await apiLogin(email.trim(), password);
      login(data.access_token, data.user);
      router.push("/upload");
    } catch (err) { setError(err.message); }
    finally { setLoading(false); }
  };

  return (
    <div style={{ display: "flex", minHeight: "100vh", backgroundColor: "#f8f9fc" }}>
      {/* Left side - Value Proposition (Hidden on small screens) */}
      <div style={{
        flex: "1 1 50%", background: "#0b0f19", color: "#ffffff",
        padding: "60px", display: "flex", flexDirection: "column", justifyContent: "space-between",
        position: "relative", overflow: "hidden"
      }} className="hidden-mobile">
        
        {/* Decorative background elements */}
        <div style={{ position: "absolute", top: "-10%", left: "-10%", width: "50%", height: "50%", background: "radial-gradient(circle, rgba(0,85,255,0.15) 0%, rgba(11,15,25,0) 70%)" }}></div>
        <div style={{ position: "absolute", bottom: "-10%", right: "-10%", width: "60%", height: "60%", background: "radial-gradient(circle, rgba(0,85,255,0.1) 0%, rgba(11,15,25,0) 70%)" }}></div>

        <div style={{ position: "relative", zIndex: 1 }}>
          <a href="/" style={{ display: "flex", alignItems: "center", gap: "10px", color: "white", textDecoration: "none", fontSize: "1.2rem", fontWeight: 700 }}>
            <span style={{ width: 32, height: 32, background: "var(--accent-primary)", borderRadius: 8, display: "flex", alignItems: "center", justifyContent: "center", fontSize: "0.8rem", fontWeight: 800 }}>AI</span>
            InterviewAI
          </a>
        </div>

        <div style={{ position: "relative", zIndex: 1, maxWidth: 480 }}>
          <div style={{ display: "inline-block", padding: "6px 16px", borderRadius: 20, background: "rgba(255,255,255,0.1)", color: "#ffffff", fontSize: "0.8rem", fontWeight: 600, marginBottom: 24, letterSpacing: "0.05em", textTransform: "uppercase" }}>
            RAG-Powered Screening
          </div>
          <h1 style={{ fontSize: "3rem", lineHeight: 1.1, marginBottom: 24, letterSpacing: "-0.03em" }}>
            Hire the top 1% with intelligent interviewing.
          </h1>
          <p style={{ fontSize: "1.1rem", color: "#9ca3af", lineHeight: 1.6, marginBottom: 40 }}>
            Automate your technical screening with AI-powered role-based interviews. Generate dynamic coding challenges directly from your company's knowledge base.
          </p>
          
          <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
            <div style={{ display: "flex" }}>
              {[1,2,3,4].map(i => (
                <div key={i} style={{ width: 40, height: 40, borderRadius: "50%", border: "2px solid #0b0f19", background: "#1e293b", marginLeft: i === 1 ? 0 : -12, display: "flex", alignItems: "center", justifyContent: "center", fontSize: "0.7rem", color: "#9ca3af" }}>
                  👤
                </div>
              ))}
            </div>
            <div style={{ fontSize: "0.9rem", color: "#9ca3af", fontWeight: 500 }}>
              Join <span style={{ color: "white" }}>10,000+</span> engineering teams
            </div>
          </div>
        </div>
        
        <div style={{ position: "relative", zIndex: 1, color: "#4b5563", fontSize: "0.85rem" }}>
          © 2025 InterviewAI Inc.
        </div>
      </div>

      {/* Right side - Form */}
      <div style={{
        flex: "1 1 50%", display: "flex", alignItems: "center", justifyContent: "center",
        padding: "40px 24px", position: "relative"
      }}>
        <div style={{ width: "100%", maxWidth: 400 }} className="animate-fade-in">
          
          <div style={{ marginBottom: 32 }}>
            <h2 style={{ fontSize: "2rem", marginBottom: 8, color: "#0b0f19" }}>
              {isSignup ? "Create an account" : "Welcome back"}
            </h2>
            <p className="text-secondary" style={{ fontSize: "1rem" }}>
              {isSignup ? "Enter your details to get started." : "Enter your credentials to access your account."}
            </p>
          </div>

          {error && (
            <div style={{
              padding: "12px 16px", borderRadius: "8px", marginBottom: 24,
              background: "rgba(239, 68, 68, 0.08)", color: "#ef4444",
              border: "1px solid rgba(239, 68, 68, 0.2)",
              fontSize: "0.9rem", display: "flex", alignItems: "center", gap: 8
            }}>
              <span style={{ fontSize: "1.2rem" }}>⚠</span> {error}
            </div>
          )}

          <form onSubmit={handleSubmit}>
            {isSignup && (
              <div className="form-group" style={{ marginBottom: 20 }}>
                <label className="form-label" style={{ fontWeight: 600, color: "#0b0f19" }}>Full Name</label>
                <input className="form-input" type="text" placeholder="John Doe"
                  value={name} onChange={e => setName(e.target.value)} required 
                  style={{ padding: "14px 16px", borderRadius: "8px", backgroundColor: "#f9fafb" }} />
              </div>
            )}

            <div className="form-group" style={{ marginBottom: 20 }}>
              <label className="form-label" style={{ fontWeight: 600, color: "#0b0f19" }}>Work Email</label>
              <input className="form-input" type="email" placeholder="you@company.com"
                value={email} onChange={e => setEmail(e.target.value)} required 
                style={{ padding: "14px 16px", borderRadius: "8px", backgroundColor: "#f9fafb" }} />
            </div>

            <div className="form-group" style={{ marginBottom: 24 }}>
              <label className="form-label" style={{ fontWeight: 600, color: "#0b0f19" }}>Password</label>
              <input className="form-input" type="password" placeholder="••••••••"
                value={password} onChange={e => setPassword(e.target.value)} required minLength={4} 
                style={{ padding: "14px 16px", borderRadius: "8px", backgroundColor: "#f9fafb" }} />
            </div>

            <button className="btn btn-primary w-full" type="submit" disabled={loading}
              style={{ width: "100%", padding: "16px", fontSize: "1rem", borderRadius: "8px", background: "#000000" }}>
              {loading ? "Please wait..." : isSignup ? "Create Account" : "Sign In"}
            </button>
          </form>

          <div style={{ textAlign: "center", marginTop: 32 }}>
            <span style={{ color: "#6b7280", fontSize: "0.95rem" }}>
              {isSignup ? "Already have an account? " : "Don't have an account? "}
            </span>
            <button onClick={() => { setIsSignup(!isSignup); setError(""); }}
              style={{
                background: "none", border: "none", cursor: "pointer",
                color: "var(--accent-primary)", fontSize: "0.95rem", fontWeight: 600,
                fontFamily: "var(--font-sans)", padding: 0
              }}>
              {isSignup ? "Sign In" : "Create one"}
            </button>
          </div>
        </div>
      </div>
      
      {/* Quick responsive fix for the hidden-mobile class */}
      <style dangerouslySetInnerHTML={{__html: `
        @media (max-width: 900px) {
          .hidden-mobile { display: none !important; }
        }
      `}} />
    </div>
  );
}
