# 🧠 Multi-Tenant Workflow Automation Platform

This project is a simplified **multi-tenant workflow automation backend**, built to demonstrate scalable architecture, secure data isolation between tenants, and asynchronous workflow execution with AI-powered steps.

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

### 🐳 Start the Stack
Run all containers (API, Celery, Redis, and PostgreSQL):

```bash
docker-compose up --build
```

Once all services are running, open the interactive API docs at:

👉 http://localhost:8000/docs

---

## 📬 Example API Requests

### 1️⃣ Register a Tenant

```bash
curl -X POST "http://localhost:8000/tenants/register" \
-H "Content-Type: application/json" \
-d '{
  "name": "TenantA"
}'
```

Response
```bash
{
  "tenant_id": "e9a3f9d8-9d0f-47cd-9b0b-32e7d6e5f2b4", 
  "name": "TenantA"
}
```

### 2️⃣ Create a Workflow

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

```bash
curl -X POST "http://localhost:8000/workflows/<workflow_id>/trigger"
```

The workflow executes asynchronously using Celery (.delay()).

### 4️⃣ Retrieve Workflow Results

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
┌──────▼──────┐ ┌──────▼──────┐ ┌──────▼──────┐
│ PostgreSQL  │ │   Redis     │ │ OpenAI API  │
│ (tenant_id) │ │ Task Queue  │ │ AI tasks    │
└──────────────┘ └────────────┘ └────────────┘
