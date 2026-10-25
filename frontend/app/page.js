"use client";

import Link from "next/link";
import { useAuth } from "@/lib/auth-context";
import AgencyHeroSection from "@/components/ui/hero-01";

export default function HomePage() {
  const { isLoggedIn } = useAuth();

  return (
    <>
      {/* Hero Section — RAG AI Interview Platform */}
      <AgencyHeroSection />

      {/* How It Works */}
      <section id="how-it-works" style={{ padding: "100px 0", background: "#f0f4f8" }}>
        <div className="container">
          <div style={{ textAlign: "center", marginBottom: 60 }}>
            <p style={{ color: "var(--accent-primary)", fontWeight: 700, fontSize: "0.85rem", marginBottom: 12, textTransform: "uppercase", letterSpacing: "0.1em" }}>How it works</p>
            <h2 style={{ fontSize: "2.5rem", color: "#0b0f19" }}>Eliminate bias from your hiring process</h2>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 30 }}>
            {[
              {
                title: "1. Upload Resume",
                desc: "Upload a candidate's resume and select the target role. Our AI instantly parses and matches skills.",
                color: "#1e293b", textCol: "white"
              },
              {
                title: "2. Dynamic Interview",
                desc: "Candidates face tailored coding, conceptual, and scenario questions generated from your knowledge base.",
                color: "#cce0ff", textCol: "#0b0f19"
              },
              {
                title: "3. Deep Insights",
                desc: "Get actionable scores on code correctness, optimization, and originality with detailed PDF reports.",
                color: "#ffffff", textCol: "#0b0f19"
              },
            ].map((step, i) => (
              <div key={i} className="glass-card animate-slide-up"
                style={{
                  background: step.color, color: step.textCol, padding: "40px 32px",
                  border: step.color === "#ffffff" ? "1px solid #e5e7eb" : "none",
                  boxShadow: "0 10px 30px rgba(0,0,0,0.05)", animationDelay: `${i * 100}ms`
                }}>
                <h3 style={{ fontSize: "1.3rem", marginBottom: 16, color: step.textCol }}>{step.title}</h3>
                <p style={{ color: step.color === "#1e293b" ? "#cbd5e1" : "var(--text-secondary)", fontSize: "0.95rem", lineHeight: 1.6 }}>{step.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section style={{ padding: "80px 0", background: "#ffffff" }}>
        <div className="container">
          <div style={{ textAlign: "center", marginBottom: 40 }}>
            <h2 style={{ fontSize: "2rem", color: "#0b0f19" }}>Global leader in automated interviewing</h2>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 40, textAlign: "center", borderTop: "1px solid #f1f5f9", paddingTop: 40 }}>
            {[
              { value: "4", label: "Roles Supported" },
              { value: "83%", label: "Time Saved on Screening" },
              { value: "7", label: "Questions per Interview" },
            ].map((stat, i) => (
              <div key={i}>
                <div style={{ fontSize: "3.5rem", fontWeight: 800, marginBottom: 8, color: "var(--accent-primary)", letterSpacing: "-0.03em" }}>{stat.value}</div>
                <div style={{ fontSize: "1rem", fontWeight: 600, color: "#0b0f19" }}>{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section style={{ padding: "100px 0", background: "#faf8f5" }}>
        <div className="container">
          <div style={{ textAlign: "center", marginBottom: 60 }}>
            <h2 style={{ fontSize: "2.5rem", marginBottom: 16, color: "#0b0f19" }}>Data-driven results</h2>
            <p style={{ color: "var(--text-secondary)", maxWidth: 600, margin: "0 auto", fontSize: "1.1rem" }}>
              Every technical interview is analyzed across multiple dimensions to ensure you hire the absolute best talent.
            </p>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 24 }}>
            {[
              { title: "Adaptive Questioning", desc: "AI adjusts question difficulty in real-time based on the candidate's previous answers." },
              { title: "Live Code Environment", desc: "Candidates write real code with language-specific syntax highlighting and formatting." },
              { title: "Plagiarism Detection", desc: "Ensure authenticity with originality checks against the provided starter code." },
              { title: "Speech Recognition", desc: "Candidates can answer conceptual questions naturally using their voice." },
              { title: "Multi-Role Support", desc: "AI/ML, Backend, Data Science, and Full Stack — each role has tailored skill sets and coding problems." },
              { title: "PDF Export", desc: "Download comprehensive interview reports to share with your hiring committee." },
            ].map((f, i) => (
              <div key={i} style={{ background: "#ffffff", padding: "32px", borderRadius: "12px", border: "1px solid #e5e7eb", boxShadow: "0 4px 12px rgba(0,0,0,0.02)" }}>
                <h3 style={{ fontSize: "1.1rem", marginBottom: 12, color: "#0b0f19" }}>{f.title}</h3>
                <p style={{ color: "var(--text-secondary)", fontSize: "0.95rem", lineHeight: 1.6 }}>{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section style={{ padding: "100px 0", background: "#ffffff", textAlign: "center" }}>
        <div className="container" style={{ maxWidth: 700 }}>
          <h2 style={{ fontSize: "2.5rem", marginBottom: 20, color: "#0b0f19" }}>Ready to streamline your interview process?</h2>
          <p style={{ color: "var(--text-secondary)", marginBottom: 40, fontSize: "1.1rem" }}>
            Join the companies transforming their hiring bandwidth with AI.
          </p>
          <Link href={isLoggedIn ? "/upload" : "/login"} className="btn btn-primary btn-lg" style={{ padding: "16px 40px", fontSize: "1.1rem" }}>
            {isLoggedIn ? "Start Screening Now" : "Book a Demo"}
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer style={{
        padding: "60px 0 40px", background: "#000000", color: "#ffffff", textAlign: "center"
      }}>
        <div className="container">
          <div style={{ fontSize: "1.5rem", fontWeight: 800, marginBottom: 20 }}>
            AI<span style={{ fontWeight: 400 }}>InterviewAI</span>
          </div>
          <p style={{ color: "#9ca3af", fontSize: "0.9rem", marginBottom: 40 }}>
            © 2025 InterviewAI — Empowering engineering teams worldwide.
          </p>
          <div className="flex gap-4 justify-center" style={{ color: "#6b7280", fontSize: "0.85rem" }}>
            <span style={{ cursor: "pointer" }}>Privacy Policy</span>
            <span style={{ cursor: "pointer" }}>Terms of Service</span>
            <span style={{ cursor: "pointer" }}>Contact Us</span>
          </div>
        </div>
      </footer>
    </>
  );
}
