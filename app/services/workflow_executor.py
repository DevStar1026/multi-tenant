from app.services.api_task import run_api_task
from app.services.ai_task import run_ai_task
from app.services.store_task import store_result
from app.models.tenant import Tenant
from sqlalchemy.orm import Session

def execute_workflow(db: Session, workflow):
    tenant = db.query(Tenant).filter(Tenant.id == workflow.tenant_id).first()
    if not tenant:
        raise Exception("Tenant not found")

    result = {}
    for step in workflow.definition["tasks"]:
        task_type = step["type"].upper()

        # API Call Task
        if task_type == "API_CALL":
            result["api"] = run_api_task(step["url"])

        # AI Task (only if allowed)
        elif task_type == "AI":
            if not tenant.allow_ai:
                result["ai"] = "AI task disabled for this tenant"
            else:
                result["ai"] = run_ai_task(step["prompt"])

        # Store Task
        elif task_type == "STORE":
            store_result(db, workflow.id, result)

    return result
