# JARVIS AI OS v1.0 — Production Release Checklist

## Pre-Release Verification

### ✅ Environment Configuration
- [ ] `SECRET_KEY` set to cryptographically random 64-char string
- [ ] `DATABASE_URL` configured for production PostgreSQL
- [ ] All AI API keys set: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`
- [ ] `ENV=production` set in environment
- [ ] `DEBUG=false` confirmed
- [ ] `CORS_ORIGINS` limited to production domain(s) only

### ✅ Database
- [ ] `alembic upgrade head` run on production database
- [ ] Default superuser created (auto-seeded on startup)
- [ ] Database backup taken before deployment
- [ ] Indexes verified for performance-critical queries

### ✅ Backend Verification
```bash
# Run from: /backend directory
cd backend

# 1. Verify all tests pass
pytest tests/ -v --cov=app --tb=short
# Expected: 180+ tests passing

# 2. Static type check
python -m mypy app/ --ignore-missing-imports || true

# 3. Security scan
bandit -r app/ -ll -q

# 4. Startup validation
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1
# Verify: http://localhost:8000/api/v1/health → {"status": "healthy"}
# Verify: http://localhost:8000/api/v1/readiness → {"status": "ready"}
# Verify: http://localhost:8000/api/v1/metrics → Prometheus text format
# Verify: http://localhost:8000/docs → Swagger UI loads
```

### ✅ Frontend Verification
```bash
# Run from: /frontend directory
cd frontend

# 1. Type check (zero errors required)
npx tsc --noEmit

# 2. Production build
npm run build
# Expected: dist/ created, no errors

# 3. Preview build
npm run preview
# Verify: http://localhost:4173 loads properly
```

### ✅ Docker Deployment
```bash
# 1. Validate compose syntax
docker compose config --quiet

# 2. Build and start all services
docker compose up -d --build

# 3. Wait for health checks
docker compose ps
# Expected: all services healthy

# 4. Run database migrations
docker compose exec backend alembic upgrade head

# 5. Verify all endpoints
curl -f http://localhost:8000/api/v1/health
curl -f http://localhost:3000
```

### ✅ Kubernetes Deployment
```bash
# Apply all manifests
kubectl apply -f k8s/

# Verify pods are running
kubectl get pods -n jarvis-os

# Check HPA (Horizontal Pod Autoscaler)
kubectl get hpa -n jarvis-os
```

### ✅ Security Checklist
- [ ] All endpoints require JWT authentication (except /health, /readiness, /docs)
- [ ] Security headers present on all responses (verify with curl -I)
- [ ] X-Request-ID correlation header working
- [ ] Rate limiting enabled (`RATE_LIMIT_ENABLED=true`)
- [ ] Default passwords changed in production
- [ ] No secrets in git history (`git log --all -S "password" -- .env`)
- [ ] SSL/TLS configured on reverse proxy (nginx/traefik)

### ✅ Observability
- [ ] `GET /api/v1/metrics` returns Prometheus metrics
- [ ] Structured logs visible in `docker compose logs backend`
- [ ] X-Request-ID headers visible in responses

---

## Rollback Procedure

If issues occur after deployment:

```bash
# 1. Revert to previous Docker image
docker compose down
docker pull jarvis-backend:previous-tag
docker compose up -d

# 2. Revert database (if schema changes)
docker compose exec backend alembic downgrade -1

# 3. Git rollback
git revert HEAD
git push origin main
```

---

## Release Tag
```bash
git tag -a v1.0.0 -m "JARVIS AI OS v1.0.0 — Production Release"
git push origin v1.0.0
```

---

## Deployment Verification Matrix

| Check | Command | Expected |
|-------|---------|----------|
| Backend health | `curl /api/v1/health` | `{"status":"healthy"}` |
| Readiness | `curl /api/v1/readiness` | `{"status":"ready"}` |
| Metrics | `curl /api/v1/metrics` | Prometheus text |
| Auth | `POST /api/v1/auth/login` | JWT token |
| JARVIS execute | `POST /api/v1/jarvis/execute` | Orchestration result |
| Security headers | `curl -I /api/v1/health` | X-Frame-Options: DENY |
| Frontend | `curl http://localhost:3000` | 200 HTML |
| DB connection | `pg_isready -U jarvis_admin` | `accepting connections` |
