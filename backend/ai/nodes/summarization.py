import asyncio
import logging

from backend.ai import llm
from backend.ai.workflow_state import EstimationState
from backend.models.errors import JobError
from backend.models.job import EstimationStage


logger = logging.getLogger(__name__)

async def summarize(state: EstimationState) -> EstimationState:
    logger.info("Started writing summary of the document content.")
    if state.progress_callback:
        await asyncio.to_thread(state.progress_callback, state.job_id, EstimationStage.SUMMARIZE, None)

    if not state.text:
        return state

    try:
        text = state.text
        state.summary = await llm.summarize_document(text)
        logger.info("Finished writing summary of the document content.")
        return state
    except Exception as ex:
        logger.error("Error while writing summary of the document content.", exc_info=ex)
        raise JobError("summarization", "Error while writing summary of the document content.")