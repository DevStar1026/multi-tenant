from celery import Celery
from app.core.config import REDIS_URL
from app.core.database import SessionLocal, Base, engine
from app.models import tenant, workflow  
from app.models.workflow import Workflow
from app.services.workflow_executor import execute_workflow

celery = Celery("tasks", broker=REDIS_URL)

# (optional in dev)
Base.metadata.create_all(bind=engine)

@celery.task
def run_workflow_task(workflow_id):
    db = SessionLocal()
    try:
        wf = db.query(Workflow).filter(Workflow.id == workflow_id).first()
        if wf:
            execute_workflow(db, wf)
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()
