# Setup Guide: AI RAG Interviewer

This guide will help you set up and run the AI RAG Interviewer project on your local machine.

## Prerequisites
- **Python 3.10 or higher**
- **Node.js 18 or higher**
- **Git**
- **Gemini API Key** (Get one from [Google AI Studio](https://aistudio.google.com/))

---

## 1. Environment Configuration
Navigate to the project root and create a `.env` file based on the example.

1.  Open your terminal in the `rag Project` directory.
2.  Copy `.env.example` to `.env`:
    ```powershell
    cp .env.example .env
    ```
3.  Open `.env` and paste your **Gemini API Key**:
    ```env
    GEMINI_API_KEY=your_actual_key_here
    ```

---

## 2. Backend Setup (FastAPI)
The backend handles the AI logic, RAG pipeline, and database.

1.  **Create a Virtual Environment**:
    ```powershell
    python -m venv venv
    ```
2.  **Activate the Environment**:
    ```powershell
    .\venv\Scripts\activate
    ```
3.  **Install Dependencies**:
    ```powershell
    pip install -r backend/requirements.txt
    ```
4.  **Run the Backend**:
    ```powershell
    uvicorn backend.main:app --reload
    ```
    *The backend will be available at `http://localhost:8000`.*

---

## 3. Frontend Setup (Next.js)
The frontend provides the user interface for the interview system.

1.  **Navigate to the frontend directory**:
    ```powershell
    cd frontend
    ```
2.  **Install Node Modules**:
    ```powershell
    npm install
    ```
3.  **Run the Development Server**:
    ```powershell
    npm run dev
    ```
    *The frontend will be available at `http://localhost:3000`.*

---

## 4. Initial Ingestion (Optional)
If you need to process the knowledge base documents for the first time:
- The system is designed to initialize the database on startup.
- Ensure the `knowledge/` folder contains the PDF/Docx files you want the AI to learn from.

---

## Troubleshooting
- **Database Errors**: If you encounter SQLite errors, delete the `backend/interview.db` file and restart the backend to let it re-initialize.
- **Port Conflicts**: Ensure ports `8000` (backend) and `3000` (frontend) are not being used by other applications.
- **Python Imports**: Always run the `uvicorn` command from the root `rag Project` directory to ensure module paths are resolved correctly.
