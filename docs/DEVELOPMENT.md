# JARVIS AI Operating System - Developer Setup Guide

This guide outlines step-by-step instructions to set up, run, test, and contribute to the JARVIS AI OS foundation services.

---

## Prerequisites

- **Python**: `3.11` or `3.12`
- **Node.js**: `20+` & `npm`
- **Docker & Docker Compose**: (Optional, for containerized local dev)
- **PostgreSQL**: `16+` (Optional, SQLite fallback is included out of the box)

---

## 1. Backend Setup (`backend/`)

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. Install production and development dependencies:
   ```bash
   pip install -r requirements.txt
   pip install pytest pytest-asyncio pytest-cov ruff mypy
   ```

4. Launch backend development server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

5. Verify API & Interactive Documentation:
   - OpenAPI Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
   - Health Route: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

6. Run backend automated test suite:
   ```bash
   pytest tests/ -v
   ```

---

## 2. Frontend Setup (`frontend/`)

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install NPM packages:
   ```bash
   npm install
   ```

3. Launch Vite development server:
   ```bash
   npm run dev
   ```

4. Access UI in browser at [http://localhost:3000](http://localhost:3000).

5. Type check and build production bundle:
   ```bash
   npm run build
   ```

---

## 3. Desktop Shell Setup (`desktop/`)

1. Navigate to the desktop directory:
   ```bash
   cd desktop
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Launch Electron app:
   ```bash
   npm start
   ```

---

## 4. Full Stack via Docker Compose

To launch PostgreSQL, FastAPI Backend, and Nginx Frontend simultaneously:

```bash
docker-compose up --build
```
