import asyncio
from typing import List

from backend.ai.workflow_state import EstimationState
from backend.models.job import EstimationStage
from backend.models.project import ProjectTaskWithContext


async def retrieve(state: EstimationState) -> EstimationState:
    """
    Поиск контекста для задач. Добавление найденной информации об оценке задач в контекст для последующей оценке.
    :param state: бегунок для workflow
    :return: возвращает объект state, который будет использоваться на следующем этапе workflow.
    """
    if state.progress_callback:
        await asyncio.to_thread(state.progress_callback, state.job_id, EstimationStage.RETRIEVAL, None)

    if not state.phases:
        state.tasks_with_context = []
        return state

    # TODO реализовать поиск в векторном хранилище по каждой задаче.
    tasks: List[ProjectTaskWithContext] = []
    for phase in state.phases:
        tasks.extend(phase.build_tasks_with_context())

    state.tasks_with_context = tasks
    return state