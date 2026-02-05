import asyncio
from pathlib import Path

from backend.adapter.reader.factory import reader_factory
from backend.ai.workflow_state import EstimationState
from backend.models.errors import JobError
from backend.models.job import EstimationStage
from backend.utils import log_utils


logger = log_utils.get_logger()

async def extract_document_content(state: EstimationState) -> EstimationState:
    logger.info("Started reading the content of the document.")
    if state.progress_callback:
        await asyncio.to_thread(state.progress_callback, state.job_id, EstimationStage.EXTRACTION, None)

    try:
        file_path = state.file_path
        file_type = _get_file_type(file_path)
        reader = reader_factory.create(file_type)
        state.text = reader.read(file_path)
        logger.info("Finished reading the content of the document.")
        return state
    except Exception as ex:
        logger.error("Error while reading the content of the document.", exc_info=ex)
        raise JobError("extraction", "Error while reading the content of the document.")

def _get_file_type(file_path: str) -> str:
    """
    Определяет тип файла по расширению (в нижнем регистре).
    """
    ext = Path(file_path).suffix.lower()
    return ext.lstrip('.')