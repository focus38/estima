import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException, Depends, UploadFile
from langgraph.graph.state import CompiledStateGraph
from starlette.responses import FileResponse

from backend import config
from backend.app_service import get_job_manager, get_estimator_graph
from backend.service.job_manager import EstimatorJobManager

estimator_router = APIRouter()


# Static frontend
@estimator_router.get("/")
async def index():
    return FileResponse("frontend/index.html")


@estimator_router.post("/upload")
async def upload_file(
        file: UploadFile,
        job_manager: EstimatorJobManager = Depends(get_job_manager),
        estimator_graph: CompiledStateGraph = Depends(get_estimator_graph)
):
    file_ext = file.filename.split(".")[-1].lower()
    if not file_ext in config.ALLOWED_FILE_EXTENSIONS:
        raise HTTPException(400, "Unsupported file format")

    job_id = uuid.uuid4()
    upload_path = config.UPLOAD_DIR / f"{job_id}_{file.filename}"
    with open(upload_path, "wb") as f:
        f.write(await file.read())

    settings_json = {}
    # Запуск фоновой задачи
    await job_manager.start_job(estimator_graph, job_id, upload_path, settings_json)
    return {"job_id": str(job_id)}


@estimator_router.get("/status/{job_id}")
async def get_status(job_id: str, job_manager: EstimatorJobManager = Depends(get_job_manager)):
    try:
        uuid_id = uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(400, "Invalid job_id")
    status = job_manager.get_status(uuid_id)
    if not status:
        raise HTTPException(404, "Job not found")
    return status


@estimator_router.get("/result/{job_id}")
async def get_result(job_id: str, job_manager: EstimatorJobManager = Depends(get_job_manager)):
    uuid_id = uuid.UUID(job_id)
    result = job_manager.get_result(uuid_id)
    if not result:
        raise HTTPException(404, "Result not ready or not found")
    return result


@estimator_router.get("/download/{filename}")
async def download_file(filename: str):
    path = Path("data/results") / filename
    if not path.exists():
        raise HTTPException(404, "File not found")
    return FileResponse(path, filename=filename)
