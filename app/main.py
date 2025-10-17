from fastapi import FastAPI, Request, HTTPException
from app.api import tenants, workflows
from app.core.database import Base, engine, SessionLocal
from app.models.tenant import Tenant

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
    public_paths = ["/", "/docs", "/openapi.json", "/tenants/register"]
    if str(request.url.path) in public_paths:
        return await call_next(request)

    tenant_id = request.headers.get("X-Tenant-ID")
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Missing X-Tenant-ID header")

    db = SessionLocal()
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    db.close()

    if not tenant:
        raise HTTPException(status_code=404, detail="Invalid tenant ID")

    request.state.tenant_id = tenant_id
    return await call_next(request)
