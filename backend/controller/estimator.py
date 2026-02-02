import json
import uuid
from pathlib import Path

from fastapi import Form
from fastapi import APIRouter, HTTPException, UploadFile, BackgroundTasks
from pydantic import ValidationError
from starlette.responses import FileResponse

from backend import config
from backend.ai.workflow_state import EstimationState
from backend.models.api import EstimationRequest
from backend.service.estimate_job import (
    start_estimate_job, get_status_estimate_job, get_result_estimate_job
)

estimator_router = APIRouter()


# Static frontend
@estimator_router.get("/")
async def index():
    return FileResponse("frontend/index.html")


@estimator_router.post("/estimate")
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


@estimator_router.get("/status/{job_id}")
async def get_status(job_id: str):
    try:
        uuid_id = uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(400, "Invalid job_id")
    status = get_status_estimate_job(uuid_id)
    if not status:
        raise HTTPException(404, "Job not found")
    return status


@estimator_router.get("/result/{job_id}")
async def get_result(job_id: str):
    uuid_id = uuid.UUID(job_id)
    result = get_result_estimate_job(uuid_id)
    if not result:
        raise HTTPException(404, "Result not ready or not found")
    return result


@estimator_router.get("/download/{filename}")
async def download_file(filename: str):
    path = Path("data/results") / filename
    if not path.exists():
        raise HTTPException(404, "File not found")
    return FileResponse(path, filename=filename)
