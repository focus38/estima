import asyncio
from pathlib import Path

from backend.adapter.reader.factory import reader_factory
from backend.ai.workflow_state import EstimationState
from backend.models.job import EstimationStage


async def extract_document_content(state: EstimationState) -> EstimationState:
    if state.progress_callback:
        await asyncio.to_thread(state.progress_callback, state.job_id, EstimationStage.EXTRACTION, None)

    file_path = state.file_path
    file_type = _get_file_type(file_path)
    reader = reader_factory.create(file_type)
    state.text = reader.read(file_path)
    return state

def _get_file_type(file_path: str) -> str:
    """
    Определяет тип файла по расширению (в нижнем регистре).
    """
    ext = Path(file_path).suffix.lower()
    return ext.lstrip('.')