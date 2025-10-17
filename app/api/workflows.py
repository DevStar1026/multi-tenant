from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import cast, String
from app.core.database import get_db
from app.models.workflow import Workflow
from app.models.tenant import Tenant
from app.utils.rate_limiter import check_rate_limit
from app.celery_worker import run_workflow_task
from pydantic import BaseModel
from typing import List, Dict

router = APIRouter(prefix="/workflows", tags=["Workflows"])

class WorkflowCreate(BaseModel):
    tenant_id: str
    name: str
    definition: dict

@router.post("/")
def create_workflow(
    payload: WorkflowCreate, 
    tenant_id: str = Header(..., alias="X-Tenant-ID"),
    db: Session = Depends(get_db)
):
    data = payload.dict()

    if data["tenant_id"] != tenant_id:
        raise HTTPException(
            status_code=403,
            detail="Tenant ID mismatch between header and payload."
        )
        
    wf = Workflow(
        tenant_id=data["tenant_id"],
        name=data["name"],
        definition=data["definition"]
    )
    db.add(wf)
    db.commit()
    db.refresh(wf)
    return {"workflow_id": wf.id}

@router.post("/{workflow_id}/trigger")
def trigger_workflow(
    workflow_id: str, 
    tenant_id: str = Header(..., alias="X-Tenant-ID"),
    db: Session = Depends(get_db)
):
    check_rate_limit(tenant_id, limit=20, window=60)

    workflow = (
        db.query(Workflow)
        .filter(
            cast(Workflow.id, String) == str(workflow_id),
            cast(Workflow.tenant_id, String) == str(tenant_id),
        )
        .first()
    )
    if not workflow:
        raise HTTPException(
            status_code=403,
            detail="Workflow does not belong to this tenant or does not exist"
        )

    run_workflow_task.delay(workflow_id)
    return {"status": "Workflow triggered", "workflow_id": workflow_id}

@router.get("/{workflow_id}/result")
def get_result(
    workflow_id: str, 
    tenant_id: str = Header(..., alias="X-Tenant-ID"),
    db: Session = Depends(get_db)
):
    wf = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")

    if str(wf.tenant_id) != tenant_id:
        raise HTTPException(status_code=403, detail="Unauthorized: cannot access workflow of another tenant")

    return {"workflow_id": str(wf.id), "result": wf.result}
