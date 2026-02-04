import asyncio
import logging
from typing import List

from backend.ai.workflow_state import EstimationState
from backend.models.errors import JobError
from backend.models.job import EstimationStage
from backend.models.project import ProjectTaskWithContext


logger = logging.getLogger(__name__)

async def retrieve(state: EstimationState) -> EstimationState:
    """
    Поиск контекста для задач. Добавление найденной информации об оценке задач в контекст для последующей оценке.
    :param state: бегунок для workflow
    :return: возвращает объект state, который будет использоваться на следующем этапе workflow.
    """
    logger.info("Started searching context for tasks.")
    if state.progress_callback:
        await asyncio.to_thread(state.progress_callback, state.job_id, EstimationStage.RETRIEVAL, None)

    if not state.phases:
        state.tasks_with_context = []
        return state

    try:
        # TODO реализовать поиск в векторном хранилище по каждой задаче.
        tasks: List[ProjectTaskWithContext] = []
        for phase in state.phases:
            tasks.extend(phase.build_tasks_with_context())

        state.tasks_with_context = tasks
        logger.info("Finished searching context for tasks.")
        return state
    except Exception as ex:
        logger.error("Error while searching context for tasks.", exc_info=ex)
        raise JobError("retrieval", "Error while searching context for tasks.")
