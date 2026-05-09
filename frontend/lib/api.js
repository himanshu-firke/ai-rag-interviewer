const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

function getToken() {
  if (typeof window === "undefined") return null;
  try {
    const saved = localStorage.getItem("auth");
    if (saved) return JSON.parse(saved).token;
  } catch {}
  return null;
}

function authHeaders() {
  const token = getToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function apiRequest(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const config = {
    ...options,
    headers: {
      ...(options.body instanceof FormData ? {} : { 'Content-Type': 'application/json' }),
      ...authHeaders(),
      ...options.headers,
    },
  };
  const response = await fetch(url, config);
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }
  return response.json();
}

// Auth
export async function signup(name, email, password) {
  return apiRequest('/api/auth/signup', {
    method: 'POST', body: JSON.stringify({ name, email, password }),
  });
}

export async function login(email, password) {
  return apiRequest('/api/auth/login', {
    method: 'POST', body: JSON.stringify({ email, password }),
  });
}

export async function getMe() {
  return apiRequest('/api/auth/me');
}

// Session
export async function createSession(role, resumeFile) {
  const formData = new FormData();
  formData.append('role', role);
  formData.append('resume', resumeFile);
  return apiRequest('/api/session/create', { method: 'POST', body: formData });
}

export async function getSession(sessionId) {
  return apiRequest(`/api/session/${sessionId}`);
}

// Interview
export async function startInterview(sessionId) {
  return apiRequest(`/api/interview/${sessionId}/start`, { method: 'POST' });
}

export async function submitAnswer(sessionId, answerText) {
  return apiRequest(`/api/interview/${sessionId}/answer`, {
    method: 'POST', body: JSON.stringify({ answer_text: answerText }),
  });
}

export async function updateAnswer(sessionId, questionId, answerText) {
  return apiRequest(`/api/interview/${sessionId}/update-answer/${questionId}`, {
    method: 'PUT', body: JSON.stringify({ answer_text: answerText }),
  });
}

export async function getAllQuestions(sessionId) {
  return apiRequest(`/api/interview/${sessionId}/questions`);
}

export async function submitAllAnswers(sessionId) {
  return apiRequest(`/api/interview/${sessionId}/submit-all`, { method: 'POST' });
}

export async function endInterview(sessionId) {
  return apiRequest(`/api/interview/${sessionId}/end`, { method: 'POST' });
}

// Report
export async function getReport(sessionId) {
  return apiRequest(`/api/report/${sessionId}`);
}

export async function exportReport(sessionId) {
  return apiRequest(`/api/report/${sessionId}/export`);
}

export function getPdfReportUrl(sessionId) {
  return `${API_BASE}/api/report/${sessionId}/export-pdf`;
}

// History
export async function getHistory() {
  return apiRequest('/api/session/history/all');
}
