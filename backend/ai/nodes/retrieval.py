import asyncio
from typing import List, Any, Dict

from backend.ai.workflow_state import EstimationState
from backend.models.errors import JobError
from backend.models.job import EstimationStage
from backend.models.project import ProjectTaskWithContext
from backend.storage.vector_store import ChromaStore
from backend.utils import log_utils


logger = log_utils.get_logger()

async def retrieve(state: EstimationState) -> EstimationState:
    """
    Поиск контекста для задач. Добавление найденной информации об оценке задач в контекст для последующей оценке.
    :param state: Объект, связывающий узлы между собой.
    :return: Возвращает объект state, который будет использоваться на следующем этапе workflow.
    """
    logger.info("Started searching context for tasks.")
    if state.progress_callback:
        await asyncio.to_thread(state.progress_callback, state.job_id, EstimationStage.RETRIEVAL, None)

    if not state.phases:
        state.tasks_with_context = []
        return state

    try:
        tasks: List[ProjectTaskWithContext] = []
        store = ChromaStore()

        k = len(state.roles)
        for phase in state.phases:
            for t in phase.tasks:
                tasks.append(ProjectTaskWithContext(
                    phase_name=phase.name,
                    task_name=t.name,
                    context="")
                )
        queries: List[str] = [t.task_name for t in tasks]
        documents = await store.query_batch(queries, k) # List[List[Dict]]
        for i in range(len(documents)):
            context = _build_context_str(documents[i])
            tasks[i].context = context

        state.tasks_with_context = tasks
        logger.info("Finished searching context for tasks.")
        return state
    except Exception as ex:
        logger.error("Error while searching context for tasks.", exc_info=ex)
        raise JobError("retrieval", "Error while searching context for tasks.")

def _build_context_str(documents: List[Dict[str, Any]]) -> str:
    parts: List[str] = []
    for doc in documents:
        context = doc.get("document", "")
        parts.append(context)
        metadata = doc.get("metadata", {})
        if metadata:
            estimate = metadata.get("estimate", None)
            if estimate:
                parts.append(f"Оценка трудозатрат: {estimate}")
            best_practice = metadata.get("best_practice", None)
            if best_practice:
                parts.append(f"Best practice: {best_practice}")
        parts.append("")

    return "\n".join(parts)