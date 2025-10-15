🧭 Architecture Justification
1️⃣ Multi-Tenancy

The platform uses a shared-schema, tenant-ID isolation pattern.
Each record (tenant, workflow, result) carries a tenant_id field, ensuring every query and stored item is automatically scoped to its tenant.
This model is the simplest and safest starting point for an MVP while remaining easy to evolve into per-schema or per-database isolation if required.
It fully satisfies the client’s request for secure, multi-tenant data separation.

2️⃣ Workflow Automation

Workflows are stored as JSON definitions describing ordered tasks.
Each task can be:

API Call Task – performs external GET/POST requests

AI Task – calls an LLM (OpenAI API by default)

Store Task – persists results back to PostgreSQL

This modular design allows tenants to build flexible automations and makes it easy to extend the engine with new task types later (e-mail, DB query, etc.).

3️⃣ Asynchronous Execution & Scalability

Workflows execute asynchronously through Celery + Redis.

run_workflow_task.delay() queues work instantly, keeping API responses fast.

Each worker runs independently, so scaling is achieved simply by adding containers (docker-compose scale worker=n).
This meets the client’s requirement for horizontal scalability and efficient background processing.

4️⃣ API Endpoints

FastAPI exposes a clear REST interface:

Endpoint	Purpose
POST /tenants/register	Register tenant
POST /workflows	Create workflow
POST /workflows/{id}/trigger	Launch async execution
GET /workflows/{id}/result	Retrieve tenant-scoped results

All endpoints map directly to the specification and use modern OpenAPI docs via /docs.

5️⃣ Observability & Metrics

Each Celery job logs execution steps and tenant IDs.
A lightweight metrics endpoint (or log aggregation) can count executions and compute average durations per tenant, fulfilling the observability requirement.

6️⃣ Bonus Features (Extensibility)

The architecture already accommodates:

Feature toggles (allow_ai flag on Tenant)

Rate limiting via FastAPI middleware

Data export per tenant ID

CI/CD integration thanks to Dockerized services

These options can be added without redesigning core components.

7️⃣ Deployment & Maintainability

Docker Compose orchestrates four independent services (API, worker, Redis, Postgres).
This separation simplifies CI/CD pipelines, monitoring, and fault isolation.
Stateless API containers and horizontally scalable workers ensure the platform can grow from a few to hundreds of tenants with minimal reconfiguration.


⚙️ How to Run and Test the System
🧰 Prerequisites

Make sure you have installed:

Docker & Docker Compose

Python 3.10+ (optional if you run locally)

An OpenAI API Key (optional, only required if you use the AI task)

🚀 Running the System

Clone or unzip the repository

git clone https://github.com/yourusername/multi-tenant-platform.git
cd multi-tenant-platform


Start the stack

docker-compose up --build


This command will start:

FastAPI app at http://localhost:8000

PostgreSQL for persistence

Redis for Celery queue

Celery worker for background workflow execution

Access API documentation
Open your browser and go to:

http://localhost:8000/docs


You’ll see all available API endpoints with live testing support (Swagger UI).

🧪 Testing the API

Below are minimal cURL examples that walk through the entire workflow.

🧩 Step 1 — Register a Tenant
curl -X POST "http://localhost:8000/tenants/register?name=TenantA"


Response:

{
  "tenant_id": "7c1b4a33-1cfa-4ea3-bd29-fd5a94e1a72e",
  "name": "TenantA"
}

🧩 Step 2 — Create a Workflow

Example workflow (API + AI + Store):

curl -X POST "http://localhost:8000/workflows" \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "7c1b4a33-1cfa-4ea3-bd29-fd5a94e1a72e",
    "name": "Weather Summary",
    "definition": {
      "tasks": [
        { "type": "API_CALL", "url": "https://api.agify.io?name=Alice" },
        { "type": "AI", "prompt": "Summarize this API result into one sentence." },
        { "type": "STORE" }
      ]
    }
  }'


Response:

{ "workflow_id": "e9987a74-47a8-4b3f-bc6f-77f8791d0202" }

🧩 Step 3 — Trigger the Workflow
curl -X POST "http://localhost:8000/workflows/e9987a74-47a8-4b3f-bc6f-77f8791d0202/trigger"


Response:

{ "status": "Workflow triggered" }


✅ The job runs asynchronously in the background via Celery.

🧩 Step 4 — Retrieve Results

Wait a few seconds, then:

curl -X GET "http://localhost:8000/workflows/e9987a74-47a8-4b3f-bc6f-77f8791d0202/result"


Example Response:

{
  "result": {
    "api": { "name": "Alice", "age": 28, "count": 12345 },
    "ai": "The user Alice is predicted to be about 28 years old according to the API."
  }
}

🧩 Step 5 — Create a Second Tenant

To test isolation:

curl -X POST "http://localhost:8000/tenants/register?name=TenantB"


Now create workflows for TenantB — all their data will remain fully isolated.

🧠 Testing Notes

Logs in the Docker console show Celery workers processing tasks per tenant:

[TenantA] Executing workflow e9987a74...
[TenantA] API_CALL complete
[TenantA] AI summary generated
[TenantA] Results stored successfully


You can run multiple tenants concurrently to test isolation and scaling.

To observe scaling, run:

docker-compose up --scale worker=3


Celery will distribute jobs across 3 workers automatically.
