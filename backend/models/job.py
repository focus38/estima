from enum import Enum
from uuid import UUID, uuid4
from datetime import datetime
from zoneinfo import ZoneInfo

from pydantic import BaseModel

class EstimationStage(str, Enum):
    PENDING = "PENDING"
    EXTRACTION = "EXTRACTION"
    SUMMARIZE = "SUMMARIZE"
    DECOMPOSITION = "DECOMPOSITION"
    RETRIEVAL = "RETRIEVAL"
    ESTIMATION = "ESTIMATION"
    PREPARE_RESULT = "PREPARE_RESULT"
    DONE = "DONE"
    FAILED = "FAILED"

    @property
    def progress(self) -> int:
        mapping = {
            EstimationStage.PENDING: 0,
            EstimationStage.EXTRACTION: 10,
            EstimationStage.SUMMARIZE: 25,
            EstimationStage.DECOMPOSITION: 45,
            EstimationStage.RETRIEVAL: 55,
            EstimationStage.ESTIMATION: 65,
            EstimationStage.PREPARE_RESULT: 95,
            EstimationStage.DONE: 100,
            EstimationStage.FAILED: 100,
        }
        return mapping.get(self, 0)

class JobInfo(BaseModel):
    id: UUID = uuid4()
    created_at: datetime = datetime.now(tz=ZoneInfo("UTC"))
    estimation_stage: EstimationStage = EstimationStage.PENDING
    progress: float = 0.0
    error: str | None = None

class JobResult(BaseModel):
    job_id: UUID
    is_success: bool