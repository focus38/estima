from typing import Callable
from uuid import UUID

from backend import config
from backend.ai.workflow import estimator_graph
from backend.ai.workflow_state import EstimationState
from backend.models.api import EstimationRequest
from backend.models.job import EstimationStage, JobResult


async def process_job(
        job_id: UUID,
        file_path: str,
        settings: EstimationRequest,
        update_status: Callable[[UUID, EstimationStage, str | None], None]
) -> JobResult:
    roles = settings.roles if settings.roles else config.DEFAULT_ROLES
    models = settings.models if settings.models else config.DEFAULT_ESTIMATION_MODELS
    state = EstimationState(job_id=job_id, file_path=file_path, models=models, roles=roles)
    state.progress_callback = lambda _id, s, e: update_status(_id, s, e)

    result = await estimator_graph.ainvoke(input=state)
    excel_file_path = result.get("excel_file_path", "")
    is_success = True if excel_file_path else False
    return _build_result(job_id, is_success)

def _build_result(job_id: UUID, is_success: bool) -> JobResult:
    return JobResult(job_id=job_id, is_success=is_success)