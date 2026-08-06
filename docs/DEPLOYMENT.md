# JARVIS AI Operating System - Production Deployment Guide

Guide for deploying JARVIS AI OS Foundation services using Docker, PostgreSQL, and Nginx.

---

## Production Architecture

```
                    +----------------------------------------+
                    |           Nginx Web Server             |
                    |       (Static Assets & Reverse Proxy)  |
                    +-------------------+--------------------+
                                        | /api/v1
                                        v
                    +-------------------+--------------------+
                    |       FastAPI Async App Server         |
                    |   (Uvicorn, Gunicorn, Gevent/UVLoop)   |
                    +-------------------+--------------------+
                                        |
                                        v
                    +-------------------+--------------------+
                    |    PostgreSQL 16 High-Availability     |
                    |    (Async Connection Pool asyncpg)     |
                    +----------------------------------------+
```

---

## 1. Environment Secrets

Copy `.env.example` to `.env` and set secure credentials:

```bash
cp .env.example .env
```

Ensure the following variables are configured:
- `SECRET_KEY`: Long, cryptographically random secret string (min 32 characters).
- `POSTGRES_USER`: Database username.
- `POSTGRES_PASSWORD`: Database password.
- `POSTGRES_DB`: Database name.

---

## 2. Docker Compose Deployment

Launch services in detached background mode:

```bash
docker-compose up -d --build
```

Verify running containers:

```bash
docker-compose ps
```

View container logs:

```bash
docker-compose logs -f
```

---

## 3. Production Verification Checklist

1. Check Backend Health Endpoint:
   ```bash
   curl -i http://localhost:8000/api/v1/health
   ```
   *Expected Output*: `200 OK`, `{"status":"HEALTHY",...}`

2. Check Database Readiness:
   ```bash
   curl -i http://localhost:8000/api/v1/health/readiness
   ```
   *Expected Output*: `200 OK`, `{"status":"READY","database":"CONNECTED",...}`

3. Access Frontend Web Console at `http://localhost:3000`. Log in with default admin seeded credentials (`admin@jarvis.ai` / `admin12345`).
