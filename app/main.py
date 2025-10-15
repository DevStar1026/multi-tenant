from fastapi import FastAPI
from app.api import tenants, workflows
from app.core.database import Base, engine
from app.models import tenant, workflow

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Multi-Tenant Workflow Platform")

app.include_router(tenants.router)
app.include_router(workflows.router)

@app.get("/")
def root():
    return {"message": "Multi-Tenant Workflow Platform running"}
