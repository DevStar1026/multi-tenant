import time, asyncio
from app.services.api_task import run_api_task
from app.services.ai_task import run_ai_task
from app.services.store_task import store_result
from app.models.tenant import Tenant
from sqlalchemy.orm import Session

async def execute_task(step):
    if step["type"] == "API_CALL":
        return ("api", run_api_task(step["url"]))
    elif step["type"] == "AI":
        return ("ai", run_ai_task(step["prompt"]))
    else:
        return (step["type"].lower(), None)

def execute_workflow(db: Session, workflow):
    tenant = db.query(Tenant).filter(Tenant.id == workflow.tenant_id).first()
    if not tenant:
        raise Exception("Tenant not found")

    result = {}
    start_time = time.time()

    async def run_all_tasks():
        tasks = []
        for step in workflow.definition.get("tasks", []):
            if step["type"].upper() == "AI" and not tenant.allow_ai:
                result["ai"] = "AI disabled for this tenant"
                continue
            tasks.append(execute_task(step))
        # Run all tasks concurrently
        completed = await asyncio.gather(*tasks)
        for key, value in completed:
            result[key] = value

    asyncio.run(run_all_tasks())

    result["execution_time"] = round(time.time() - start_time, 3)
    store_result(db, workflow.id, result)
    return result
