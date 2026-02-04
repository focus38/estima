import json
import uuid

from fastapi import Form
from fastapi import APIRouter, HTTPException, UploadFile, BackgroundTasks
from pydantic import ValidationError

from backend import config
from backend.models.api import EstimationRequest
from backend.service.estimate_job import start_estimate_job


estimator_router = APIRouter()

@estimator_router.post("/api/estimate")
async def upload_file(
        file: UploadFile,
        settings: str = Form(...),
        background_tasks: BackgroundTasks = None
):
    try:
        request_json = json.loads(settings)
        estimation_request = EstimationRequest(**request_json)
    except (json.JSONDecodeError, ValidationError) as e:
        raise HTTPException(status_code=400, detail=f"Invalid settings: {e}")

    file_ext = file.filename.split(".")[-1].lower()
    if not file_ext in config.ALLOWED_FILE_EXTENSIONS:
        raise HTTPException(400, "Unsupported file format")

    job_id = uuid.uuid4()
    file_path = config.UPLOAD_DIR / f"{job_id}_{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Запуск фоновой задачи
    background_tasks.add_task(start_estimate_job, job_id, str(file_path), estimation_request)
    return {"job_id": str(job_id)}
