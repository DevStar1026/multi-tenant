from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
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
def export_tenant_data(
    tenant_id: str,
    TenantId: str = Header(..., alias="X-Tenant-ID"),
    db: Session = Depends(get_db)
):
    if TenantId != tenant_id:
        raise HTTPException(
            status_code=403,
            detail="Tenant ID mismatch between header and payload."
        )

    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first() 
    if not tenant: 
        raise HTTPException(status_code=404, detail="Tenant not found")
    
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
def toggle_ai(
    tenant_id: str, 
    enable: bool, 
    TenantId: str = Header(..., alias="X-Tenant-ID"),
    db: Session = Depends(get_db)
):
    if TenantId != tenant_id:
        raise HTTPException(
            status_code=403,
            detail="Tenant ID mismatch between header and payload."
        )
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    tenant.allow_ai = enable
    db.commit()
    return {"tenant_id": tenant_id, "allow_ai": tenant.allow_ai}

@router.get("/{tenant_id}/metrics")
def tenant_metrics(
    tenant_id: str, 
    TenantId: str = Header(..., alias="X-Tenant-ID"),
    db: Session = Depends(get_db)
):
    if TenantId != tenant_id:
        raise HTTPException(
            status_code=403,
            detail="Tenant ID mismatch between header and payload."
        )
    
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()

    total_workflows = db.query(func.count(Workflow.id)).filter(Workflow.tenant_id == tenant_id).scalar()
    avg_execution_time = db.query(
        func.avg(func.coalesce(Workflow.result["execution_time"].as_float(), 0))
    ).scalar() or 0.0

    return {
        "tenant_id": tenant_id,
        "tenant_name": tenant.name,
        "total_workflows": total_workflows,
        "average_execution_time_sec": round(avg_execution_time, 2),
    }