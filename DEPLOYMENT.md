# MediBot Deployment Guide

This guide will walk you through deploying the MediBot application for **free** using:
1.  **MongoDB Atlas** (Database)
2.  **Render.com** (Backend)
3.  **Vercel** (Frontend)

---

## 1. Database Setup (MongoDB Atlas)

1.  Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) and sign up/login.
2.  Create a **New Project** named "MediBot".
3.  Click **Create Deployment** and choose **M0 (Free Tier)**.
4.  **Security Quickstart**:
    *   Create a database user (username/password). **Save these!**
    *   Add your IP address to the access list (or `0.0.0.0/0` to allow access from anywhere, required for Render).
5.  Go to **Database** > **Connect** > **Drivers**.
6.  Copy the **Connection String**. It looks like:
    `mongodb+srv://<username>:<password>@cluster0.mongodb.net/?retryWrites=true&w=majority`
    *   Replace `<password>` with the user password you created.

---

## 2. Backend Deployment (Render.com)

1.  Push your code to **GitHub** (if you haven't already).
2.  Go to [Render Dashboard](https://dashboard.render.com/).
3.  Click **New +** > **Web Service**.
4.  Connect your GitHub repository.
5.  **Configure the Service**:
    *   **Name**: `medibot-backend`
    *   **Region**: Choose one close to you (e.g., Frankfurt, Singapore).
    *   **Branch**: `main`
    *   **Root Directory**: `backend` (Important! This tells Render where the python code is).
    *   **Runtime**: `Python 3`
    *   **Build Command**: `pip install -r requirements.txt`
    *   **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port 10000`
    *   **Instance Type**: Free

6.  **Environment Variables** (Click "Advanced" or "Environment"):
    Add the following keys and values from your local `.env` file:
    *   `MONGODB_URL`: (Your MongoDB Atlas connection string)
    *   `DB_NAME`: `medibot`
    *   `SECRET_KEY`: (Generate a strong random string)
    *   `ALGORITHM`: `HS256`
    *   `ACCESS_TOKEN_EXPIRE_MINUTES`: `30`
    *   `GOOGLE_API_KEY`: (Your Gemini API Key)
    *   `MAIL_USERNAME`: (Your Gmail address)
    *   `MAIL_PASSWORD`: (Your Gmail App Password)
    *   `MAIL_FROM`: (Your Gmail address)
    *   `MAIL_PORT`: `587`
    *   `MAIL_SERVER`: `smtp.gmail.com`
    *   `FRONTEND_URL`: (Leave empty for now, we will update this after deploying frontend)

7.  Click **Create Web Service**.
8.  Wait for the deployment to finish. Copy the **Service URL** (e.g., `https://medibot-backend.onrender.com`).

---

## 3. Frontend Deployment (Vercel)

1.  Go to [Vercel Dashboard](https://vercel.com/dashboard).
2.  Click **Add New...** > **Project**.
3.  Import your GitHub repository.
4.  **Configure Project**:
    *   **Framework Preset**: Vite
    *   **Root Directory**: Click "Edit" and select `frontend`.
5.  **Environment Variables**:
    *   `VITE_API_URL`: Paste your **Render Backend URL** (e.g., `https://medibot-backend.onrender.com`).
        *   *Note: Do not add a trailing slash `/`.*

6.  Click **Deploy**.
7.  Wait for deployment. You will get a domain (e.g., `https://medibot-frontend.vercel.app`).

---

## 4. Final Configuration

1.  Go back to **Render Dashboard** > `medibot-backend` > **Environment**.
2.  Add/Update the `FRONTEND_URL` variable:
    *   `FRONTEND_URL`: `https://medibot-frontend.vercel.app` (Your Vercel URL)
3.  **Save Changes**. Render will redeploy automatically.

**Congratulations! Your MediBot is now live!** 🚀
