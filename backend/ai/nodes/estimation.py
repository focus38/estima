import asyncio

from backend.ai import llm
from backend.ai.workflow_state import EstimationState
from backend.models.job import EstimationStage


async def estimate(state: EstimationState) -> EstimationState:
    if state.progress_callback:
        await asyncio.to_thread(state.progress_callback, state.job_id, EstimationStage.ESTIMATION, None)

    if not state.roles:
        state.estimates = []
        return state
    if not state.tasks_with_context:
        state.estimates = []
        return state
    if not state.models:
        state.estimates = []
        return state

    roles = state.roles
    summary = state.summary
    tasks = state.tasks_with_context
    model_name = state.models[state.current_model_index]
    model_estimation = await llm.estimate(model_name, summary, tasks, roles)

    state.current_model_index = state.current_model_index + 1
    state.estimates.append({
        model_name: model_estimation # TaskEstimation
    })

    return state