from fastapi import FastAPI, Request
from app.api import tenants, workflows
from app.core.database import Base, engine

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Multi-Tenant Workflow Automation Platform")

# Include routers
app.include_router(tenants.router)
app.include_router(workflows.router)

@app.get("/")
def root():
    return {"message": "Multi-Tenant Workflow Automation Platform running"}

@app.middleware("http")
async def tenant_header_middleware(request: Request, call_next):
    tenant_id = request.headers.get("X-Tenant-ID")
    if tenant_id:
        request.state.tenant_id = tenant_id
    response = await call_next(request)
    return response
