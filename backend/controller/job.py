import uuid

from fastapi import APIRouter, HTTPException
from starlette.responses import FileResponse

from backend import config
from backend.service.estimate_job import get_status_estimate_job, get_result_estimate_job

job_router = APIRouter()

@job_router.get("/api/job/status/{job_id}")
async def get_status(job_id: str):
    try:
        uuid_id = uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(400, "Invalid job_id")
    status = get_status_estimate_job(uuid_id)
    if not status:
        raise HTTPException(404, "Job not found")
    return status

@job_router.get("/api/job/result/{job_id}")
async def get_result(job_id: str):
    uuid_id = uuid.UUID(job_id)
    result = get_result_estimate_job(uuid_id)
    if not result:
        raise HTTPException(404, "Result not ready or not found")
    return result

@job_router.get("/api/job/download/{job_id}")
async def download_file(job_id: str):
    filename = f"estima_result_{job_id}.xlsx"
    path = config.RESULTS_DIR / filename
    if not path.exists():
        raise HTTPException(404, "File not found")
    return FileResponse(path, filename=filename)
