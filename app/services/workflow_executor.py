from app.services.api_task import run_api_task
from app.services.ai_task import run_ai_task
from app.services.store_task import store_result
from sqlalchemy.orm import Session

def execute_workflow(db: Session, workflow):
    result = {}
    for step in workflow.definition["tasks"]:
        if step["type"] == "API_CALL":
            result["api"] = run_api_task(step["url"])
        elif step["type"] == "AI":
            result["ai"] = run_ai_task(step["prompt"])
        elif step["type"] == "STORE":
            store_result(db, workflow.id, result)
    return result
