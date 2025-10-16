from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.workflow import Workflow
from app.models.tenant import Tenant
from app.utils.rate_limiter import check_rate_limit
from app.celery_worker import run_workflow_task
from pydantic import BaseModel

router = APIRouter(prefix="/workflows", tags=["Workflows"])

class WorkflowCreate(BaseModel):
    tenant_id: str
    name: str
    definition: dict

@router.post("/")
def create_workflow(payload: WorkflowCreate, db: Session = Depends(get_db)):
    data = payload.dict()
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
def trigger_workflow(workflow_id: str, tenant_id: str = Header(..., alias="X-Tenant-ID")):
    check_rate_limit(tenant_id, limit=20, window=60)
    run_workflow_task.delay(workflow_id)
    return {"status": "Workflow triggered"}

@router.get("/{workflow_id}/result")
def get_result(workflow_id: str, db: Session = Depends(get_db)):
    wf = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not wf:
        return {"error": "Workflow not found"}
    return {"workflow_id": str(wf.id), "result": wf.result}
