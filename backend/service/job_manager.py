import asyncio
from uuid import UUID
from typing import Dict, Optional

from langgraph.graph.state import CompiledStateGraph

from backend.models.job import JobInfo, JobResult, JobStatus
from backend.service.processing import process_job

class EstimatorJobManager:
    def __init__(self):
        self.jobs: Dict[UUID, JobInfo] = {}
        self.results: Dict[UUID, JobResult] = {}

    async def start_job(self,
                        estimator_graph: CompiledStateGraph,
                        job_id: UUID,
                        file_path: str,
                        settings_json: Dict):
        self.jobs[job_id] = JobInfo(id=job_id)
        # Запускаем фоновую задачу без await (запустил и забыл).
        asyncio.create_task(self._run_job(estimator_graph, job_id, file_path, settings_json))

    async def _run_job(self, estimator_graph: CompiledStateGraph, job_id: UUID, file_path: str, settings_json: Dict):
        try:
            # Обновляем статус
            self._update_status(job_id, JobStatus.estimating, 10.0)
            result = await process_job(estimator_graph, job_id, file_path, settings_json, self._update_status)
            self.results[job_id] = result
            self._update_status(job_id, JobStatus.done, 100.0)
        except Exception as e:
            self._update_status(job_id, JobStatus.failed, 0.0, str(e))

    def _update_status(self, job_id: UUID, status: JobStatus, progress: float, error: str | None = None):
        if job_id in self.jobs:
            self.jobs[job_id].status = status
            self.jobs[job_id].progress = progress
            self.jobs[job_id].error = error

    def get_status(self, job_id: UUID) -> Optional[JobInfo]:
        return self.jobs.get(job_id)

    def get_result(self, job_id: UUID) -> Optional[JobResult]:
        return self.results.get(job_id)
