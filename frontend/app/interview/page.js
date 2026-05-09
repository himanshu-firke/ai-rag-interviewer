"use client";

import { useState, useEffect, useRef, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import {
  startInterview, submitAnswer, updateAnswer,
  getAllQuestions, submitAllAnswers, getSession
} from "@/lib/api";

function InterviewContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const sessionId = searchParams.get("session");

  const [sessionData, setSessionData] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [finalSubmitting, setFinalSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [totalQuestions, setTotalQuestions] = useState(7);
  const [isListening, setIsListening] = useState(false);
  const recognitionRef = useRef(null);

  useEffect(() => {
    if (!sessionId) { router.push("/upload"); return; }
    async function init() {
      try {
        const session = await getSession(sessionId);
        setSessionData(session);
        setTotalQuestions(session.total_questions);
        const result = await startInterview(sessionId);
        setTotalQuestions(result.total_questions);
        if (result.questions && result.questions.length > 0) {
          setQuestions(result.questions);
          const firstUnanswered = result.questions.findIndex(q => !q.answer);
          const idx = firstUnanswered >= 0 ? firstUnanswered : 0;
          setCurrentIndex(idx);
          setAnswer(result.questions[idx]?.answer || "");
        }
      } catch (err) { setError(err.message); }
      finally { setLoading(false); }
    }
    init();
  }, [sessionId, router]);

  // Speech-to-text
  useEffect(() => {
    if (typeof window !== "undefined" && ("SpeechRecognition" in window || "webkitSpeechRecognition" in window)) {
      const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
      const recognition = new SR();
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = "en-US";
      recognition.onresult = (e) => {
        let transcript = "";
        for (let i = 0; i < e.results.length; i++) transcript += e.results[i][0].transcript;
        setAnswer(prev => {
          const base = prev.replace(/\[listening\.\.\.\]$/i, "").trim();
          return base ? base + " " + transcript : transcript;
        });
      };
      recognition.onerror = () => setIsListening(false);
      recognition.onend = () => setIsListening(false);
      recognitionRef.current = recognition;
    }
    return () => { if (recognitionRef.current) try { recognitionRef.current.stop(); } catch(e) {} };
  }, []);

  const toggleListening = () => {
    if (!recognitionRef.current) { alert("Speech recognition not supported. Use Chrome."); return; }
    if (isListening) { recognitionRef.current.stop(); setIsListening(false); }
    else { recognitionRef.current.start(); setIsListening(true); }
  };

  const currentQ = questions[currentIndex];
  const isCoding = currentQ?.type === "coding";
  const allAnswered = questions.length >= totalQuestions && questions.every(q => q.answer && q.answer.trim());

  const handleSubmitAnswer = async () => {
    if (!answer.trim() || submitting) return;
    setSubmitting(true); setError("");
    try {
      if (currentQ.answer) {
        await updateAnswer(sessionId, currentQ.id, answer.trim());
        setQuestions(prev => prev.map((q, i) => i === currentIndex ? { ...q, answer: answer.trim() } : q));
      } else {
        const result = await submitAnswer(sessionId, answer.trim());
        setQuestions(prev => prev.map((q, i) => i === currentIndex ? { ...q, answer: answer.trim() } : q));
        if (result.next_question) {
          setQuestions(prev => [...prev, { ...result.next_question, answer: null }]);
        }
      }
      const updatedQs = questions.map((q, i) => i === currentIndex ? { ...q, answer: answer.trim() } : q);
      const nextUnanswered = updatedQs.findIndex((q, i) => i > currentIndex && !q.answer);
      if (nextUnanswered >= 0) { setCurrentIndex(nextUnanswered); setAnswer(""); }
      else if (updatedQs.length < totalQuestions) { setCurrentIndex(updatedQs.length); setAnswer(""); }
    } catch (err) { setError(err.message); }
    finally { setSubmitting(false); }
  };

  const handleFinalSubmit = async () => {
    if (!allAnswered || finalSubmitting) return;
    setFinalSubmitting(true); setError("");
    try {
      await submitAllAnswers(sessionId);
      router.push(`/results?session=${sessionId}`);
    } catch (err) { setError(err.message); setFinalSubmitting(false); }
  };

  const navigateToQuestion = (index) => {
    setCurrentIndex(index);
    setAnswer(questions[index]?.answer || (questions[index]?.code_template || ""));
  };

  // When switching to a coding question, pre-fill with template
  useEffect(() => {
    if (currentQ && currentQ.type === "coding" && !currentQ.answer && !answer) {
      setAnswer(currentQ.code_template || "");
    }
  }, [currentIndex]);

  if (loading) {
    return (
      <div className="page">
        <div className="container" style={{ maxWidth: 900, textAlign: "center", paddingTop: 100 }}>
          <div className="skeleton" style={{ width: 60, height: 60, borderRadius: "50%", margin: "0 auto 20px" }} />
          <div className="skeleton" style={{ width: 300, height: 24, margin: "0 auto 12px" }} />
          <p className="text-muted mt-4">Preparing your interview...</p>
        </div>
      </div>
    );
  }

  const progress = (questions.filter(q => q.answer).length / totalQuestions) * 100;

  return (
    <div className="page">
      <div className="container" style={{ maxWidth: 920 }}>
        {/* Header */}
        <div className="glass-card mb-4 animate-fade-in" style={{ padding: "16px 24px" }}>
          <div className="flex justify-between items-center mb-2">
            <div className="flex items-center gap-3">
              <span className="tag tag-primary">{sessionData?.role || "Interview"}</span>
              <span className="text-secondary" style={{ fontSize: "0.85rem" }}>
                {questions.filter(q => q.answer).length}/{totalQuestions} answered
              </span>
            </div>
            {allAnswered && (
              <button className="btn btn-primary" onClick={handleFinalSubmit} disabled={finalSubmitting}
                style={{ padding: "8px 20px" }}>
                {finalSubmitting ? "Evaluating..." : "Submit All & Get Results"}
              </button>
            )}
          </div>
          <div className="progress-bar">
            <div className="progress-bar-fill" style={{ width: `${progress}%` }} />
          </div>
        </div>

        {/* Question Navigation Pills */}
        <div className="flex gap-2 mb-4" style={{ flexWrap: "wrap" }}>
          {questions.map((q, i) => (
            <button key={i} onClick={() => navigateToQuestion(i)}
              title={`Q${i+1}: ${q.type || 'question'}`}
              style={{
                width: 38, height: 38, borderRadius: "50%", border: "none", cursor: "pointer",
                fontFamily: "var(--font-sans)", fontSize: "0.75rem", fontWeight: 700,
                background: i === currentIndex ? "var(--gradient-primary)"
                  : q.answer ? "rgba(16, 185, 129, 0.2)" : "var(--bg-glass)",
                color: i === currentIndex ? "white" : q.answer ? "var(--accent-success)" : "var(--text-muted)",
                border: i === currentIndex ? "none" : "1px solid var(--border-default)",
                transition: "all var(--transition-fast)",
                position: "relative",
              }}>
              {i + 1}
              {q.type === "coding" && (
                <span style={{
                  position: "absolute", bottom: -2, right: -2, width: 12, height: 12,
                  borderRadius: "50%", background: "#6366f1", fontSize: "0.45rem",
                  display: "flex", alignItems: "center", justifyContent: "center", color: "white",
                }}>&lt;/&gt;</span>
              )}
            </button>
          ))}
          {questions.length < totalQuestions && (
            <span className="text-muted" style={{ fontSize: "0.75rem", alignSelf: "center" }}>
              +{totalQuestions - questions.length} more
            </span>
          )}
        </div>

        {/* Current Question */}
        {currentQ && (
          <div className="glass-card mb-4 animate-slide-up">
            <div className="flex items-center gap-2 mb-3">
              <span style={{
                width: 32, height: 32, borderRadius: "50%", background: "var(--gradient-primary)",
                display: "flex", alignItems: "center", justifyContent: "center",
                fontSize: "0.8rem", fontWeight: 700, color: "white",
              }}>{currentQ.number || currentIndex + 1}</span>
              <span className="tag tag-info" style={{ fontSize: "0.65rem" }}>{currentQ.topic || "Question"}</span>
              <span className="tag tag-warning" style={{ fontSize: "0.65rem" }}>{currentQ.difficulty || "medium"}</span>
              {isCoding && <span className="tag tag-primary" style={{ fontSize: "0.65rem" }}>CODING</span>}
              {currentQ.answer && <span className="tag tag-success" style={{ fontSize: "0.65rem" }}>Answered</span>}
            </div>

            <p style={{ fontSize: "1.05rem", fontWeight: 500, lineHeight: 1.6, marginBottom: 16, whiteSpace: "pre-wrap" }}>
              {currentQ.text}
            </p>

            {/* Coding question: show language badge */}
            {isCoding && currentQ.expected_language && (
              <div className="flex items-center gap-2 mb-3">
                <span style={{
                  padding: "3px 10px", borderRadius: 6,
                  background: "rgba(99, 102, 241, 0.1)", color: "var(--accent-primary-light)",
                  fontSize: "0.75rem", fontWeight: 600, fontFamily: "var(--font-mono)",
                }}>
                  {currentQ.expected_language}
                </span>
                <span className="text-muted" style={{ fontSize: "0.75rem" }}>
                  Write your solution below
                </span>
              </div>
            )}

            {error && (
              <div style={{
                padding: "8px 12px", borderRadius: "var(--radius-sm)",
                background: "rgba(239, 68, 68, 0.1)", color: "var(--accent-danger)",
                marginBottom: 12, fontSize: "0.85rem",
              }}>{error}</div>
            )}

            {/* Answer Input — Code Editor or Text */}
            <div style={{ position: "relative" }}>
              <textarea
                className={isCoding ? "" : "form-textarea"}
                placeholder={isCoding ? "Write your code here..." : "Type your answer... or use the mic"}
                value={answer} onChange={(e) => setAnswer(e.target.value)}
                disabled={submitting}
                spellCheck={!isCoding}
                style={isCoding ? {
                  width: "100%", minHeight: 240, padding: "16px",
                  fontFamily: "var(--font-mono)", fontSize: "0.85rem",
                  background: "#0d1117", color: "#c9d1d9",
                  border: "1px solid rgba(99, 102, 241, 0.3)",
                  borderRadius: "var(--radius-md)",
                  lineHeight: 1.6, resize: "vertical", outline: "none",
                  tabSize: 4,
                } : {
                  minHeight: 140, paddingRight: 50, resize: "vertical",
                  width: "100%", padding: "12px 16px", fontFamily: "var(--font-sans)",
                  fontSize: "0.95rem", color: "var(--text-primary)",
                  background: "var(--bg-glass)", border: "1px solid var(--border-default)",
                  borderRadius: "var(--radius-md)", outline: "none",
                }}
              />
              {/* Mic Button (only for non-coding) */}
              {!isCoding && (
                <button onClick={toggleListening}
                  title={isListening ? "Stop" : "Speech-to-text"}
                  style={{
                    position: "absolute", right: 12, top: 12, width: 36, height: 36,
                    borderRadius: "50%", border: "none", cursor: "pointer",
                    background: isListening ? "rgba(239, 68, 68, 0.2)" : "var(--bg-glass)",
                    color: isListening ? "var(--accent-danger)" : "var(--text-muted)",
                    display: "flex", alignItems: "center", justifyContent: "center",
                    animation: isListening ? "pulse 1.5s infinite" : "none",
                    border: isListening ? "2px solid var(--accent-danger)" : "1px solid var(--border-default)",
                  }}>
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" />
                    <path d="M19 10v2a7 7 0 0 1-14 0v-2" /><line x1="12" y1="19" x2="12" y2="23" />
                    <line x1="8" y1="23" x2="16" y2="23" />
                  </svg>
                </button>
              )}
            </div>

            {isListening && <p style={{ fontSize: "0.8rem", color: "var(--accent-danger)", marginTop: 4 }}>Listening...</p>}

            <div className="flex gap-3 mt-4">
              <button className="btn btn-primary" onClick={handleSubmitAnswer}
                disabled={submitting || !answer.trim()} style={{ flex: 1 }}>
                {submitting ? "Saving..." : currentQ.answer ? "Update Answer" : "Save & Next"}
              </button>
              {currentIndex > 0 && (
                <button className="btn btn-secondary" onClick={() => navigateToQuestion(currentIndex - 1)}>Prev</button>
              )}
              {currentQ.answer && currentIndex < questions.length - 1 && (
                <button className="btn btn-secondary" onClick={() => navigateToQuestion(currentIndex + 1)}>Next</button>
              )}
            </div>
          </div>
        )}

        {/* Final Submit */}
        {allAnswered && (
          <div className="glass-card animate-slide-up" style={{ textAlign: "center", borderColor: "var(--border-accent)" }}>
            <h3 style={{ marginBottom: 8 }}>All Questions Answered!</h3>
            <p className="text-secondary mb-4" style={{ fontSize: "0.9rem" }}>
              Review using the pills above, then submit for AI evaluation.
            </p>
            <button className="btn btn-primary btn-lg" onClick={handleFinalSubmit} disabled={finalSubmitting}>
              {finalSubmitting ? "Evaluating all answers..." : "Submit & Get Results →"}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default function InterviewPage() {
  return (
    <Suspense fallback={<div className="page"><div className="container" style={{ maxWidth: 900, textAlign: "center", paddingTop: 100 }}><p className="text-muted">Loading...</p></div></div>}>
      <InterviewContent />
    </Suspense>
  );
}
