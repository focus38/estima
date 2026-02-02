import asyncio

from backend.ai import llm
from backend.ai.workflow_state import EstimationState
from backend.models.job import EstimationStage


async def decompose(state: EstimationState) -> EstimationState:
    if state.progress_callback:
        await asyncio.to_thread(state.progress_callback, state.job_id, EstimationStage.DECOMPOSITION, None)

    if not state.text:
        state.phases = []
        return state

    if not state.roles:
        state.phases = []
        return state

    text = state.text
    roles = state.roles
    state.phases = await llm.decompose_document(text, roles)
    return state