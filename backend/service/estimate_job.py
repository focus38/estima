import logging
from typing import Dict, Optional
from uuid import UUID

from backend.models.api import EstimationRequest
from backend.models.job import JobInfo, EstimationStage, JobResult
from backend.service.processing import process_job

_jobs: Dict[UUID, JobInfo] = {}
_results: Dict[UUID, JobResult] = {}
logger = logging.getLogger(__name__)

async def start_estimate_job(job_id: UUID, file_path: str, settings: EstimationRequest) -> None:
    try:
        _jobs[job_id] = JobInfo(id=job_id)
        # Обновляем статус
        stage = _jobs[job_id].estimation_stage if _jobs[job_id].estimation_stage else EstimationStage.PENDING
        _update_status(job_id, stage)

        result = await process_job(job_id, file_path, settings, _update_status)
        _results[job_id] = result
        _update_status(job_id, EstimationStage.DONE)
    except Exception as ex:
        logger.error("Error while start estimate job.", exc_info=ex)
        _update_status(job_id, EstimationStage.FAILED, str(ex))

def get_status_estimate_job(job_id: UUID) -> Optional[JobInfo]:
    return _jobs.get(job_id)

def get_result_estimate_job(job_id: UUID) -> Optional[JobResult]:
    return _results.get(job_id)

def _update_status(job_id: UUID, status: EstimationStage, error: str | None = None):
    if job_id in _jobs:
        _jobs[job_id].estimation_stage = status
        _jobs[job_id].progress = status.progress
        _jobs[job_id].error = error
