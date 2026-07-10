# 🚀 Deployment Guide — AI RAG Interviewer

Complete step-by-step deployment guide for the AI-Powered Role-Based Candidate Screening System.

| Component | Platform | URL Pattern |
|:----------|:---------|:------------|
| **Frontend** | Vercel | `https://your-app.vercel.app` |
| **Backend** | Render | `https://your-service.onrender.com` |

> **Deploy Order**: Backend first → Frontend second (frontend needs the backend URL).

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Part 1: Local Setup](#part-1-local-setup)
- [Part 2: Deploy Backend on Render](#part-2-deploy-backend-on-render)
- [Part 3: Deploy Frontend on Vercel](#part-3-deploy-frontend-on-vercel)
- [Part 4: Post-Deployment Configuration](#part-4-post-deployment-configuration)
- [Part 5: RAG Pipeline & Knowledge Base](#part-5-rag-pipeline--knowledge-base)
- [Part 6: Verification Checklist](#part-6-verification-checklist)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

| Requirement | Where to Get |
|:------------|:-------------|
| **GitHub Account** | Push this repo to GitHub (already at `himanshu-firke/ai-rag-interviewer`) |
| **Vercel Account** | [vercel.com](https://vercel.com) — sign up with GitHub |
| **Render Account** | [render.com](https://render.com) — sign up with GitHub |
| **Groq API Key** | [console.groq.com/keys](https://console.groq.com/keys) — free tier |
| **Gemini API Key** | [aistudio.google.com/apikey](https://aistudio.google.com/apikey) — free tier |
| **Python 3.10+** | For local setup only |
| **Node.js 18+** | For local setup only |

---

## Part 1: Local Setup

### 1.1 Clone & Configure Environment

```bash
git clone https://github.com/himanshu-firke/ai-rag-interviewer.git
cd ai-rag-interviewer

# Create environment file
cp .env.example .env
```

Edit `.env` with your actual API keys:

```env
LLM_PROVIDER=groq
GROQ_API_KEY=gsk_your_actual_groq_key
GEMINI_API_KEY=AIza_your_actual_gemini_key
JWT_SECRET=generate-a-random-string-here
```

> 💡 Generate a strong JWT secret:
> ```bash
> python -c "import secrets; print(secrets.token_urlsafe(32))"
> ```

### 1.2 Backend Setup

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows PowerShell)
.\venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt
```

### 1.3 Frontend Setup

```bash
cd frontend
npm install
cd ..
```

### 1.4 Run Locally

Open **two terminals** from the project root:

```bash
# Terminal 1 — Backend (from project root)
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 — Frontend
cd frontend && npm run dev
```

| Service | Local URL |
|:--------|:----------|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| Swagger Docs | http://localhost:8000/docs |

### 1.5 Verify Local Setup

1. Open http://localhost:8000 — should return `{"status": "healthy", ...}`
2. Open http://localhost:8000/api/health — shows vector store stats
3. Open http://localhost:3000 — landing page should load
4. Sign up → Upload resume → Start interview → Verify questions generate

---

## Part 2: Deploy Backend on Render

### 2.1 Create Render Web Service

1. Go to [dashboard.render.com](https://dashboard.render.com)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repo: `himanshu-firke/ai-rag-interviewer`
4. Configure the service:

| Setting | Value |
|:--------|:------|
| **Name** | `ai-interviewer-backend` |
| **Region** | Oregon (US West) or closest to you |
| **Branch** | `main` |
| **Root Directory** | _(leave empty — use repo root)_ |
| **Runtime** | Python |
| **Build Command** | `pip install -r backend/requirements.txt` |
| **Start Command** | `gunicorn backend.main:app -w 2 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT` |
| **Plan** | Free |

> ⚠️ **Critical**: The Root Directory must be empty (repo root), NOT `backend/`. This is because all Python imports use `backend.*` module paths (e.g., `from backend.config import settings`).

### 2.2 Set Environment Variables

In the Render dashboard, go to **Environment** tab and add:

| Key | Value | Notes |
|:----|:------|:------|
| `LLM_PROVIDER` | `groq` | |
| `GROQ_API_KEY` | `gsk_your_key` | 🔑 Your actual key |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` | |
| `GEMINI_API_KEY` | `AIza_your_key` | 🔑 Your actual key |
| `GEMINI_MODEL` | `gemini-2.0-flash` | |
| `EMBEDDING_MODEL` | `text-embedding-004` | |
| `JWT_SECRET` | _(auto-generate)_ | Click "Generate" |
| `DATABASE_URL` | `sqlite:///./backend/interview.db` | |
| `CHROMA_PATH` | `./backend/chroma_db` | |
| `KNOWLEDGE_BASE_PATH` | `./knowledge` | |
| `CORS_ORIGINS` | `["http://localhost:3000"]` | Update after frontend deploy |
| `PYTHON_VERSION` | `3.11.12` | |
| `PYTHONPATH` | `.` | Ensures backend module resolution |

### 2.3 Add Persistent Disk (Recommended)

Without a disk, Render's free tier **wipes the filesystem on every deploy**. This means:
- ❌ SQLite database resets
- ❌ ChromaDB vector store resets (re-ingestion every time)

**To add a disk** (requires paid plan):

1. Go to **Disks** tab → **Add Disk**
2. Mount Path: `/opt/render/project/src/backend`
3. Size: 1 GB

> 💡 **Free tier workaround**: On the free plan, the knowledge base PDFs are in the repo and get re-ingested on each cold start automatically via the startup lifespan. The SQLite DB will reset, but for a demo this is acceptable — users just re-register.

### 2.4 Deploy & Verify

1. Click **"Create Web Service"**
2. Wait for the build to complete (2–4 minutes)
3. Your backend URL will be: `https://ai-interviewer-backend.onrender.com`
4. Visit `https://YOUR-RENDER-URL.onrender.com/` — should return:
   ```json
   {"status": "healthy", "service": "AI Interview Screening System", "version": "1.0.0"}
   ```
5. Visit `https://YOUR-RENDER-URL.onrender.com/docs` — Swagger UI should load

> ⚠️ **Free tier cold starts**: Render free tier spins down after 15 minutes of inactivity. First request after idle takes ~30–60 seconds.

📋 **Copy your Render URL** — you'll need it for the frontend deployment.

---

## Part 3: Deploy Frontend on Vercel

### 3.1 Create Vercel Project

1. Go to [vercel.com/new](https://vercel.com/new)
2. Click **"Import Git Repository"**
3. Select `himanshu-firke/ai-rag-interviewer`
4. Configure:

| Setting | Value |
|:--------|:------|
| **Framework Preset** | Next.js |
| **Root Directory** | `frontend` |
| **Build Command** | `npm run build` |
| **Output Directory** | _(leave default)_ |
| **Install Command** | `npm install` |

### 3.2 Set Environment Variables

Add this environment variable in Vercel's project settings:

| Key | Value | Environment |
|:----|:------|:------------|
| `NEXT_PUBLIC_API_URL` | `https://ai-interviewer-backend.onrender.com` | Production, Preview, Development |

> ⚠️ **No trailing slash!** Use `https://your-service.onrender.com` NOT `https://your-service.onrender.com/`

### 3.3 Deploy

1. Click **"Deploy"**
2. Wait for the build (1–2 minutes)
3. Your frontend URL will be: `https://your-project.vercel.app`

### 3.4 Verify Frontend

1. Visit `https://your-project.vercel.app` — landing page should load
2. Try the signup flow — it should hit your Render backend

📋 **Copy your Vercel URL** — you need it for the CORS update below.

---

## Part 4: Post-Deployment Configuration

### 4.1 Update CORS Origins on Render (CRITICAL)

After the frontend is deployed, go back to **Render Dashboard** → your backend service → **Environment**:

Update the `CORS_ORIGINS` variable:

```
["https://your-project.vercel.app"]
```

If you want to allow both local dev and production:

```
["http://localhost:3000","http://127.0.0.1:3000","https://your-project.vercel.app"]
```

**Click "Save Changes"** — Render will auto-redeploy.

> ⚠️ **Without this step**, the frontend will get CORS errors on every API call. You'll see `blocked by CORS policy` in the browser console.

### 4.2 Custom Domain (Optional)

**Vercel (Frontend)**:
1. Go to Project → Settings → Domains
2. Add your domain (e.g., `interview.yourdomain.com`)
3. Follow Vercel's DNS instructions

**Render (Backend)**:
1. Go to Service → Settings → Custom Domains
2. Add your domain (e.g., `api.yourdomain.com`)
3. Update `CORS_ORIGINS` to include the new frontend domain

---

## Part 5: RAG Pipeline & Knowledge Base

### 5.1 How Knowledge Ingestion Works

The RAG pipeline is **fully automatic**:

```
Startup → Find PDFs in knowledge/ → Extract pages → Chunk text → Generate embeddings → Store in ChromaDB
```

1. **On backend startup**, `init_db()` creates SQLite tables
2. The `knowledge/` folder contains role-specific ML textbooks (committed to the repo)
3. When a user starts an interview, `ingest_knowledge_base()` is called if needed
4. PDFs are split into 1000-char chunks with 200-char overlap
5. Each chunk is embedded using Google's `text-embedding-004` model
6. Chunks are stored in ChromaDB with deduplication (same chunk ID = no re-insert)

### 5.2 Knowledge Base Files

| File | Size | Content |
|:-----|:-----|:--------|
| `Artificial Intelligence, Machine Learning, and Deep Learning.pdf` | 5 MB | Comprehensive AI/ML textbook |
| `Bishop-Pattern-Recognition-and-Machine-Learning-2006.pdf` | 18 MB | Bishop's PRML (classic) |
| `Machine Learning For Absolute Beginners.pdf` | 2.7 MB | Beginner-friendly ML guide |

### 5.3 Adding New Knowledge

To add new PDFs to the RAG pipeline:

1. Place the PDF file in the `knowledge/` directory
2. Commit and push to GitHub
3. Render will auto-redeploy
4. The new PDF will be ingested on the next interview start

### 5.4 Verifying RAG Pipeline

After deployment, verify the pipeline:

```bash
# Check health endpoint (includes vector store stats)
curl https://YOUR-RENDER-URL.onrender.com/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "llm_provider": "groq",
  "llm_model": "llama-3.3-70b-versatile",
  "vector_store_chunks": 1500,
  "embedding": "all-MiniLM-L6-v2 (local)"
}
```

> If `vector_store_chunks` is `0`, the knowledge base hasn't been ingested yet. Start an interview to trigger ingestion.

---

## Part 6: Verification Checklist

Run through this checklist after deployment:

### Backend (Render)
- [ ] `GET /` returns `{"status": "healthy"}`
- [ ] `GET /api/health` returns vector store stats
- [ ] `GET /docs` loads Swagger UI
- [ ] `POST /api/auth/signup` creates a user
- [ ] `POST /api/auth/login` returns a JWT token

### Frontend (Vercel)
- [ ] Landing page loads with no console errors
- [ ] Signup/Login works (no CORS errors)
- [ ] Resume upload + role selection works
- [ ] Interview questions generate (RAG pipeline active)
- [ ] Can answer questions and navigate between them
- [ ] "Finish" generates evaluation report
- [ ] PDF export downloads successfully
- [ ] Interview history shows past sessions

### Integration
- [ ] CORS is configured for the Vercel domain
- [ ] All API calls from frontend reach the backend
- [ ] JWT authentication works across both platforms

---

## Troubleshooting

### CORS Errors
**Symptom**: `Access to fetch blocked by CORS policy` in browser console.
**Fix**: Update `CORS_ORIGINS` env var on Render to include your Vercel URL.

### 502 Bad Gateway on Render
**Symptom**: Render shows 502 error.
**Fix**:
1. Check Render logs for Python errors
2. Verify `PYTHONPATH=.` is set
3. Verify start command uses `backend.main:app` (not `main:app`)
4. Check that all API keys are set correctly

### "Module Not Found" Errors
**Symptom**: `ModuleNotFoundError: No module named 'backend'`
**Fix**: Ensure:
- `PYTHONPATH=.` is set in Render env vars
- Root Directory is empty (not `backend/`)
- Start command uses `backend.main:app`

### Frontend Shows Blank / API Errors
**Symptom**: Frontend loads but API calls fail.
**Fix**:
1. Verify `NEXT_PUBLIC_API_URL` is set in Vercel (no trailing slash)
2. Redeploy the frontend after adding the env var
3. Check browser console for the actual error

### ChromaDB / Vector Store Empty
**Symptom**: `vector_store_chunks: 0` in health check.
**Fix**: Start an interview session — ingestion triggers on first question generation. Check Render logs for ingestion output.

### Render Free Tier Cold Starts
**Symptom**: First request takes 30–60 seconds.
**This is normal** on Render's free tier. The service spins down after 15 min of inactivity. Options:
1. Use a paid plan ($7/month) for always-on
2. Use an external cron to ping `/` every 14 minutes
3. Accept the delay for demo purposes

### SQLite Lock Errors
**Symptom**: `database is locked` errors under load.
**Fix**: SQLite doesn't handle concurrent writes well. For production:
1. Use PostgreSQL (change `DATABASE_URL` to a Postgres connection string)
2. Update `database.py` to remove `check_same_thread=False`
3. Add `psycopg2-binary` to `requirements.txt`

---

## Architecture Reference

```
Production Setup:

┌─────────────────┐     HTTPS      ┌──────────────────────┐
│   Vercel CDN    │ ◄────────────► │  User's Browser      │
│   (Frontend)    │                └──────────────────────┘
│   Next.js SSR   │                         │
└────────┬────────┘                         │
         │ NEXT_PUBLIC_API_URL              │
         │                                  │
         ▼                                  │
┌─────────────────┐                         │
│   Render        │ ◄──────────────────────-┘
│   (Backend)     │       REST API + JWT
│   FastAPI +     │
│   Gunicorn      │
│                 │
│ ┌─────────────┐ │     ┌───────────────┐
│ │ SQLite DB   │ │     │ Groq API      │
│ │ ChromaDB    │ │────►│ (Llama 3.3)   │
│ │ Knowledge/  │ │     │ Gemini API    │
│ └─────────────┘ │     │ (Embeddings)  │
└─────────────────┘     └───────────────┘
```

---

## Environment Variable Summary

### Backend (Render)

| Variable | Required | Description |
|:---------|:---------|:------------|
| `LLM_PROVIDER` | ✅ | `groq` or `gemini` |
| `GROQ_API_KEY` | ✅ | Groq API key |
| `GROQ_MODEL` | ❌ | Default: `llama-3.3-70b-versatile` |
| `GEMINI_API_KEY` | ✅ | Gemini API key (for embeddings) |
| `GEMINI_MODEL` | ❌ | Default: `gemini-2.0-flash` |
| `EMBEDDING_MODEL` | ❌ | Default: `text-embedding-004` |
| `JWT_SECRET` | ✅ | Random secret (auto-generate on Render) |
| `DATABASE_URL` | ❌ | Default: `sqlite:///./backend/interview.db` |
| `CHROMA_PATH` | ❌ | Default: `./backend/chroma_db` |
| `KNOWLEDGE_BASE_PATH` | ❌ | Default: `./knowledge` |
| `CORS_ORIGINS` | ✅ | JSON array of allowed frontend origins |
| `PYTHON_VERSION` | ❌ | Recommended: `3.11.12` |
| `PYTHONPATH` | ✅ | Must be `.` |

### Frontend (Vercel)

| Variable | Required | Description |
|:---------|:---------|:------------|
| `NEXT_PUBLIC_API_URL` | ✅ | Full Render backend URL (no trailing slash) |
