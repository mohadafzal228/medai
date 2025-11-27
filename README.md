# MediBot - Medical AI Chatbot System

A production-grade Medical AI Chatbot built with FastAPI, MongoDB, Gemini AI, and React.

## 🚀 Quick Start (Local Development)

### Prerequisites
- Python 3.9+
- Node.js 18+
- MongoDB Atlas Account
- Google Cloud Console Account (for Gemini API)

### 1. Backend Setup
```bash
cd backend
python -m venv venv
# Windows
.\venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt

# Create .env file
cp .env.example .env
# EDIT .env with your MongoDB URL and Google API Key
```

Run the server:
```bash
uvicorn app.main:app --reload
```
Backend will run at `http://localhost:8000`.

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Frontend will run at `http://localhost:5173`.

## ☁️ Deployment Guide

### A. Backend (Render.com)
1.  Create a new **Web Service** on Render.
2.  Connect your GitHub repository.
3.  Settings:
    -   **Runtime**: Python 3
    -   **Build Command**: `pip install -r backend/requirements.txt`
    -   **Start Command**: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4.  **Environment Variables**: Add all variables from `backend/.env` (MONGODB_URL, GOOGLE_API_KEY, etc.).

### B. Frontend (Vercel)
1.  Import your project into Vercel.
2.  Settings:
    -   **Framework Preset**: Vite
    -   **Root Directory**: `frontend`
    -   **Build Command**: `npm run build`
    -   **Output Directory**: `dist`
3.  **Environment Variables**:
    -   If you hardcoded the API URL in `api.js`, update it to your Render Backend URL.
    -   Ideally, use `VITE_API_URL` in `frontend/.env` and update `api.js` to use `import.meta.env.VITE_API_URL`.

## 🔑 API Keys & Database

### MongoDB Connection String
1.  Log in to [MongoDB Atlas](https://www.mongodb.com/atlas).
2.  Create a Cluster (Free Tier).
3.  Click **Connect** > **Drivers**.
4.  Copy the connection string (e.g., `mongodb+srv://<user>:<password>@...`).
5.  Replace `<password>` with your database user password.

### Google Gemini API Key
1.  Go to [Google AI Studio](https://makersuite.google.com/app/apikey).
2.  Click **Get API key**.
3.  Create a key in a new project.
