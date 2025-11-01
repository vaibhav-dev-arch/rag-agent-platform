# 🚀 Deployment Guide

## Production Deployment Options

### Option 1: Docker Compose (Recommended for Development/Staging)

#### Prerequisites
- Docker and Docker Compose installed
- OpenAI API key

#### Steps

1. **Clone the repository**
```bash
git clone https://github.com/vaibhav-dev-arch/rag-agent-platform.git
cd rag-agent-platform
```

2. **Create `.env` file**
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

3. **Start all services**
```bash
docker-compose up -d
```

4. **Verify deployment**
```bash
# Check API health
curl http://localhost:8000/health

# Check API metrics
curl http://localhost:8000/metrics

# Access Prometheus
open http://localhost:9090

# Access Grafana (default: admin/admin)
open http://localhost:3000
```

5. **View logs**
```bash
docker-compose logs -f rag-api
```

#### Services
- **API**: `http://localhost:8000`
- **Web UI**: `http://localhost:5000`
- **PostgreSQL**: `localhost:5432`
- **Redis**: `localhost:6379`
- **Prometheus**: `http://localhost:9090`
- **Grafana**: `http://localhost:3000`

---

### Option 2: Kubernetes (Production)

#### Prerequisites
- Kubernetes cluster (minikube, GKE, EKS, AKS, etc.)
- `kubectl` configured
- OpenAI API key

#### Steps

1. **Create namespace**
```bash
kubectl apply -f kubernetes/namespace.yaml
```

2. **Create secrets**
```bash
kubectl create secret generic rag-platform-secrets \
  --from-literal=OPENAI_API_KEY=your-key \
  --from-literal=JWT_SECRET=your-secret \
  -n rag-platform
```

3. **Apply configurations**
```bash
kubectl apply -f kubernetes/configmap.yaml
kubectl apply -f kubernetes/pvc.yaml
kubectl apply -f kubernetes/deployment.yaml
kubectl apply -f kubernetes/service.yaml
kubectl apply -f kubernetes/hpa.yaml
```

4. **Verify deployment**
```bash
kubectl get pods -n rag-platform
kubectl get services -n rag-platform
kubectl logs -f deployment/rag-platform-api -n rag-platform
```

5. **Check health**
```bash
kubectl port-forward service/rag-platform-api 8000:80 -n rag-platform
curl http://localhost:8000/health
```

---

### Option 3: Docker (Single Container)

#### Steps

1. **Build image**
```bash
docker build -t rag-agent-platform .
```

2. **Run container**
```bash
docker run -d \
  -p 8000:8000 \
  -e OPENAI_API_KEY=your-key \
  -e DATABASE_URL=postgresql://user:pass@host:5432/db \
  -v $(pwd)/data:/app/data \
  --name rag-platform \
  rag-agent-platform
```

3. **Check logs**
```bash
docker logs -f rag-platform
```

---

## Environment Variables

### Required
- `OPENAI_API_KEY`: Your OpenAI API key

### Optional
- `DATABASE_URL`: PostgreSQL connection string (default: SQLite)
- `REDIS_HOST`: Redis host (default: None, uses in-memory)
- `REDIS_PORT`: Redis port (default: 6379)
- `CORS_ORIGINS`: Allowed origins (default: "*")
- `RATE_LIMIT_ENABLED`: Enable rate limiting (default: true)
- `RATE_LIMIT_REQUESTS`: Max requests per window (default: 100)
- `RATE_LIMIT_WINDOW`: Window in seconds (default: 60)
- `SENTRY_DSN`: Sentry DSN for error tracking (optional)
- `ENVIRONMENT`: Environment name (default: "production")
- `LOG_LEVEL`: Log level (default: "INFO")

---

## Health Checks

### Basic Health Check
```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "openai_configured": true,
  "index_ready": true,
  "agent_ready": true,
  "message": "API is ready"
}
```

### Detailed Health Check
```bash
curl http://localhost:8000/health/detailed
```

Includes:
- Component status
- Performance metrics
- Database connectivity
- Vector index status

---

## Monitoring

### Prometheus Metrics
- Endpoint: `/metrics`
- Scrape interval: 15s
- Metrics include:
  - HTTP requests (total, duration, status)
  - RAG queries (total, duration, status)
  - Agent queries (total, duration, status)
  - Database queries (total, duration, status)
  - Rate limit hits
  - System metrics (active connections, document count)

### Grafana Dashboards
- Access: `http://localhost:3000`
- Default credentials: `admin/admin`
- Pre-configured dashboards:
  - API Performance
  - RAG Query Metrics
  - Database Performance
  - System Health

---

## Troubleshooting

### API not starting
1. Check logs: `docker-compose logs rag-api`
2. Verify OpenAI API key: `echo $OPENAI_API_KEY`
3. Check database connectivity
4. Verify ports are not in use

### Database connection issues
1. Check PostgreSQL is running: `docker-compose ps postgres`
2. Verify connection string in `.env`
3. Check database logs: `docker-compose logs postgres`

### Performance issues
1. Check metrics: `curl http://localhost:8000/metrics`
2. Review Grafana dashboards
3. Check resource usage: `docker stats`
4. Review logs for errors

---

## Scaling

### Horizontal Scaling (Kubernetes)
- Auto-scaling configured via HPA
- Min replicas: 3
- Max replicas: 10
- Scaling based on CPU (70%) and Memory (80%)

### Vertical Scaling
- Update resource limits in `docker-compose.yml` or `kubernetes/deployment.yaml`
- Restart services

---

## Backup & Recovery

### Database Backup
```bash
# PostgreSQL
docker exec rag-postgres pg_dump -U rag_user rag_platform > backup.sql

# Restore
docker exec -i rag-postgres psql -U rag_user rag_platform < backup.sql
```

### Persistent Volumes
- Data: `/app/data`
- Output: `/app/output`
- Logs: `/app/logs`

---

## Security

### Production Checklist
- [ ] Set `CORS_ORIGINS` to specific domains
- [ ] Use strong `JWT_SECRET`
- [ ] Enable rate limiting
- [ ] Set up monitoring and alerting
- [ ] Use HTTPS (via reverse proxy)
- [ ] Secure database credentials
- [ ] Enable Sentry for error tracking
- [ ] Review and update security policies

---

*For more details, see [docs/README.md](README.md) and [docs/API_DOCUMENTATION.md](API_DOCUMENTATION.md)*

