import asyncio
from typing import List

from backend.ai import llm
from backend.ai.workflow_state import EstimationState
from backend.models.estimation import TaskEstimation
from backend.models.job import EstimationStage
from backend.utils import log_utils


logger = log_utils.get_logger()

async def estimate(state: EstimationState) -> EstimationState:
    logger.info("Started estimating tasks.")
    if state.progress_callback:
        await asyncio.to_thread(state.progress_callback, state.job_id, EstimationStage.ESTIMATION, None)

    if not state.roles:
        state.estimates = []
        state.current_model_index = state.current_model_index + 1  # Увеличиваем текущий индекс модели.
        return state
    if not state.tasks_with_context:
        state.estimates = []
        state.current_model_index = state.current_model_index + 1  # Увеличиваем текущий индекс модели.
        return state
    if not state.models:
        state.estimates = []
        state.current_model_index = state.current_model_index + 1  # Увеличиваем текущий индекс модели.
        return state

    model_name = state.models[state.current_model_index]
    model_estimation = await _estimate_by_model(model_name, state)
    state.current_model_index = state.current_model_index + 1 # Увеличиваем текущий индекс модели.
    state.estimates.append({
        model_name: model_estimation # TaskEstimation
    })

    if state.current_model_index == len(state.models):
        logger.info("Finished estimating tasks.")

    return state

async def _estimate_by_model(model_name: str, state: EstimationState) -> List[TaskEstimation]:
    logger.info(f"Started estimating tasks using the model {model_name}")
    try:
        roles = state.roles
        summary = state.summary
        tasks = state.tasks_with_context
        model_estimation = await llm.estimate(model_name, summary, tasks, roles)
        logger.info(f"Finished estimating tasks using the model {model_name}")
        return model_estimation
    except Exception as ex:
        logger.error(f"Error in the process of estimating tasks using the model {model_name}", exc_info=ex)
        return []
