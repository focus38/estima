import asyncio

from backend.ai import llm
from backend.ai.workflow_state import EstimationState
from backend.models.errors import JobError
from backend.models.job import EstimationStage
from backend.utils import log_utils

logger = log_utils.get_logger()

async def decompose(state: EstimationState) -> EstimationState:
    logger.info("Started the process of decomposing the document into tasks.")
    if state.progress_callback:
        await asyncio.to_thread(state.progress_callback, state.job_id, EstimationStage.DECOMPOSITION, None)

    if not state.text:
        state.phases = []
        return state

    if not state.roles:
        state.phases = []
        return state

    try:
        text = state.text
        roles = state.roles
        state.phases = await llm.decompose_document(text, roles)
        logger.info("Finished the process of decomposing the document into tasks.")
        return state
    except Exception as ex:
        logger.error("Error in the process of decomposing the document into tasks.", exc_info=ex)
        raise JobError("decomposition", "Error in the process of decomposing the document into tasks.")