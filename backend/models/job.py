from enum import Enum
from uuid import UUID, uuid4
from datetime import datetime
from zoneinfo import ZoneInfo

from pydantic import BaseModel

class JobStatus(str, Enum):
    pending = "pending"
    extracting = "extracting"
    summarizing = "summarizing"
    rag_lookup = "rag_lookup"
    estimating = "estimating"
    exporting = "exporting"
    done = "done"
    failed = "failed"

class JobInfo(BaseModel):
    id: UUID = uuid4()
    created_at: datetime = datetime.now(tz=ZoneInfo("UTC"))
    status: JobStatus = JobStatus.pending
    progress: float = 0.0
    error: str | None = None

class JobResult(BaseModel):
    job_id: UUID
    summary: str
    phases: list[dict]
    estimates: list[dict]
    excel_url: str