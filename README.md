# 🧠 Multi-Tenant Workflow Automation Platform

This project is a simplified **multi-tenant workflow automation backend**, built to demonstrate scalable architecture, secure data isolation between tenants, and asynchronous workflow execution with AI-powered steps.

---

## 🚀 Features

- ✅ Multi-tenant data isolation (`tenant_id`)
- ✅ Asynchronous workflow execution (Celery + Redis)
- ✅ API tasks, AI tasks, and data storage tasks
- ✅ Feature toggles per tenant (e.g., allow/disallow AI)
- ✅ Rate limiting per tenant
- ✅ Data export endpoint per tenant
- ✅ Dockerized architecture (API + Worker + DB + Redis)
- ✅ CI/CD-ready structure (GitHub Actions, containerized deployment)

---

## 🧱 Tech Stack

| Layer | Technology |
|--------|-------------|
| **Backend Framework** | FastAPI |
| **Async Worker** | Celery |
| **Queue** | Redis |
| **Database** | PostgreSQL |
| **ORM** | SQLAlchemy |
| **Containerization** | Docker Compose |
| **AI Integration** | OpenAI API |

---

## 🚀 How to Run the System

### 🧩 Prerequisites
- Docker & Docker Compose installed
- (Optional) OpenAI API key for AI task execution

### ⚙️ Environment Setup
Create a `.env` file in the project root:

```bash
DATABASE_URL=postgresql://postgres:postgres@db/postgres
REDIS_URL=redis://redis:6379/0
OPENAI_API_KEY=your_openai_api_key_here
```

### 🐳 Run the System
Run all containers (API, Celery, Redis, and PostgreSQL):

```bash
docker-compose up --build
```

Once all services are running, open the interactive API docs at:

👉 http://localhost:8000/docs

---

## 📬 Example API Requests

### 1️⃣ Register a Tenant

POST /tenants/register?name=TenantA
```bash
curl -X POST "http://localhost:8000/tenants/register?name=TenantA"
```

Response
```bash
{
  "tenant_id": "e9a3f9d8-9d0f-47cd-9b0b-32e7d6e5f2b4", 
  "name": "TenantA"
}
```

### 2️⃣ Create a Workflow

POST /workflows
```bash
curl -X POST "http://localhost:8000/workflows" \
-H "Content-Type: application/json" \
-d '{
  "tenant_id": "e9a3f9d8-9d0f-47cd-9b0b-32e7d6e5f2b4",
  "name": "WeatherSummary",
  "definition": {
    "tasks": [
      {"type": "API_CALL", "url": "https://api.weatherapi.com/v1/current.json?q=London"},
      {"type": "AI", "prompt": "Summarize the weather data in one sentence"},
      {"type": "STORE"}
    ]
  }
}'
```

### 3️⃣ Trigger Workflow Execution

POST /workflows/{workflow_id}/trigger
```bash
curl -X POST "http://localhost:8000/workflows/<workflow_id>/trigger" \
-H "X-Tenant-ID: e9a3f9d8-9d0f-47cd-9b0b-32e7d6e5f2b4"

```

The workflow executes asynchronously using Celery (.delay()).

### 4️⃣ Retrieve Workflow Results

GET /workflows/{workflow_id}/result
```bash
curl -X GET "http://localhost:8000/workflows/<workflow_id>/result"
```

Example Response
```bash
{
  "result": {
    "api": {"location": "London", "temp_c": 20},
    "ai": "The weather in London is mild and pleasant."
  }
}
```

### 5️⃣ Export Tenant Data

GET /tenants/{tenant_id}/export
```bash
curl -X GET "http://localhost:8000/tenants/e9a3f9d8-9d0f-47cd-9b0b-32e7d6e5f2b4/export"
```

Response
```bash
{
  "tenant_id": "e9a3f9d8-9d0f-47cd-9b0b-32e7d6e5f2b4",
  "exported_at": "2025-10-14T15:30:00Z",
  "workflows": [
    {
      "workflow_id": "f2b4a123-...",
      "name": "WeatherSummary",
      "definition": {...},
      "result": {...}
    }
  ]
}
```

---
## 🧠 Multi-Tenancy Model

### ✅ Model Used: Shared-Schema Multi-Tenancy

All tenants share the same database schema, and each record is tagged with a tenant_id.
This provides logical isolation between tenants while keeping infrastructure simple and scalable.

| Aspect         | Description                                                      |
| -------------- | ---------------------------------------------------------------- |
| **Isolation**  | Each tenant’s workflows and results are filtered by `tenant_id`. |
| **Efficiency** | Shared infrastructure (PostgreSQL + Redis) for all tenants.      |
| **Simplicity** | Easy to add new tenants dynamically via `/tenants/register`.     |
| **Trade-off**  | Must ensure strict tenant-based filtering in every query.        |

### Example Schema

| id | tenant_id | name            | definition | result |
| -- | --------- | --------------- | ---------- | ------ |
| 1  | TenantA   | WeatherSummary  | {...}      | {...}  |
| 2  | TenantB   | ProductInsights | {...}      | {...}  |

Tenants A and B share the same codebase and infrastructure, but each only sees their own data.

---
## 🧩 Bonus Features

### 🎛️ 1. Feature Toggles per Tenant

- Each tenant has an allow_ai flag in the tenants table.
- When allow_ai=False, AI steps are skipped with a message:

```bash
{
  "ai": "AI task disabled for this tenant"
}
```

### ⚙️ 2. Rate Limiting per Tenant

- Each tenant is limited to 20 requests per minute using a Redis-based rate limiter.
- If exceeded, the API responds:

```bash
{
  "detail": "Rate limit exceeded for this tenant"
}
```

### 💾 3. Data Export

- Endpoint: GET /tenants/{tenant_id}/export
- Returns all workflows and results for that tenant in JSON format.

### 🔁 4. CI/CD and Deployment Strategy

- Dockerized system (API, Worker, Redis, DB)
- CI/CD via GitHub Actions (sample workflow below)
- orizontal scaling via containers or Kubernetes
- Cloud deployment on AWS ECS, GCP Cloud Run, or Azure Container Apps

#### .github/workflows/deploy.yml

```bash
name: CI/CD Pipeline
on:
  push:
    branches: [main]

jobs:
  build-and-test:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest

  docker-build-and-push:
    runs-on: ubuntu-latest
    needs: build-and-test
    steps:
      - name: Checkout
        uses: actions/checkout@v3
      - name: Build Docker image
        run: docker build -t yourrepo/multi-tenant-platform .
      - name: Push to Docker Hub
        run: |
          echo ${{ secrets.DOCKERHUB_TOKEN }} | docker login -u ${{ secrets.DOCKERHUB_USER }} --password-stdin
          docker push yourrepo/multi-tenant-platform
```
---

## 📈 Scaling the System to Hundreds of Tenants

### 1️⃣ Application Layer

- Use FastAPI in stateless Docker containers behind a load balancer (e.g., NGINX, AWS ALB).
- Horizontal scaling: run multiple API containers to handle concurrent tenant traffic.

### 2️⃣ Asynchronous Workers

- Celery workers handle background workflows independently.
- Scale horizontally (multiple Celery instances consuming from Redis queues).
- Tag logs and metrics with tenant_id for observability.

### 3️⃣ Database Strategy

- Start with shared schema for simplicity.
- For large tenants, migrate to schema-per-tenant or database-per-tenant models.
- PostgreSQL supports multiple schemas efficiently.

### 4️⃣ Security & Observability

- Middleware to enforce X-Tenant-ID on all requests.
- Collect per-tenant metrics (e.g., workflow count, average duration).
- Use centralized logging (ELK / Loki) for tenant-based monitoring.

### 5️⃣ Feature Extensions

- Per-tenant feature toggles (e.g., enable/disable AI tasks)
- Rate limiting & quotas per tenant
- Data export endpoint for tenants

---

 ## 🧩 System Overview Diagram

```bash
          ┌────────────────────────┐
          │      Tenant A API      │
          │  /tenants, /workflows  │
          └────────────┬───────────┘
                       │
          ┌────────────▼───────────┐
          │       FastAPI App      │
          │ Multi-Tenant Backend   │
          │ (shared codebase)      │
          └────────────┬───────────┘
                       │
          ┌────────────▼───────────┐
          │      Celery Worker     │
          │ Executes Workflows     │
          │ (API → AI → STORE)     │
          └────────────┬───────────┘
                       │
       ┌───────────────┼────────────────┐
       │               │                │
┌──────▼──────┐ ┌──────▼──────┐ ┌───────▼─────┐
│ PostgreSQL  │ │   Redis     │ │ OpenAI API  │
│ (tenant_id) │ │ Task Queue  │ │ AI tasks    │
└─────────────┘ └─────────────┘ └─────────────┘
```
---
## 🧠 Testing via Postman
### 1. Start containers:
docker-compose up --build

### 2. Use Postman requests in order:

- Register tenant → Copy tenant_id
- Create workflow → Copy workflow_id
- Trigger workflow (with header X-Tenant-ID)
- Retrieve workflow result
- Export tenant data

### 3. Bonus Tests

- Disable AI (allow_ai=False) → test workflow
- Trigger 25+ requests quickly → get 429 Rate limit exceeded