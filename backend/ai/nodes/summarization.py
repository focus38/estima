import asyncio

from backend.ai import llm
from backend.ai.workflow_state import EstimationState
from backend.models.job import EstimationStage


async def summarize(state: EstimationState) -> EstimationState:
    if state.progress_callback:
        await asyncio.to_thread(state.progress_callback, state.job_id, EstimationStage.SUMMARIZE, None)

    if not state.text:
        return state

    text = state.text
    state.summary = await llm.summarize_document(text)
    return state