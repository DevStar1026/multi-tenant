from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from app.core.database import get_db
from app.models.tenant import Tenant
from app.models.workflow import Workflow

router = APIRouter(prefix="/tenants", tags=["Tenants"])

@router.post("/register")
def register_tenant(name: str, db: Session = Depends(get_db)):
    tenant = Tenant(name=name)
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return {"tenant_id": tenant.id, "name": tenant.name}

@router.get("/{tenant_id}/export")
def export_tenant_data(tenant_id: str, db: Session = Depends(get_db)):
    workflows = db.query(Workflow).filter(Workflow.tenant_id == tenant_id).all()
    export = [
        {
            "workflow_id": wf.id,
            "name": wf.name,
            "definition": wf.definition,
            "result": wf.result
        } for wf in workflows
    ]
    return {
        "tenant_id": tenant_id,
        "exported_at": datetime.utcnow().isoformat(),
        "workflows": export
    }

@router.put("/{tenant_id}/toggle_ai")
def toggle_ai(tenant_id: str, enable: bool, db: Session = Depends(get_db)):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    tenant.allow_ai = enable
    db.commit()
    return {"tenant_id": tenant_id, "allow_ai": tenant.allow_ai}
