from sqlalchemy.orm import Session
from app.models.workflow import Workflow

def store_result(db: Session, workflow_id, result):
    wf = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if wf:
        wf.result = result
        db.commit()
        return {"status": "stored", "workflow_id": str(wf.id)}
    return {"status": "failed"}
