from typing import List, Dict, Optional, Callable
from uuid import UUID

from pydantic import BaseModel, Field

from backend.models.estimation import TaskEstimation
from backend.models.project import ProjectPhase, ProjectTaskWithContext


class EstimationState(BaseModel):
    job_id: UUID = Field(description="Идентификатор задания.", default="")
    file_path: str = Field(description="Путь к файлу с техническим заданием.")
    models: List[str] = Field(description="Список моделей, которые будут задействованы в оценке.", default_factory=list)
    roles: List[str] = Field(description="Роли участников для реализации задания.", default_factory=list)
    text: str = Field(description="Текст брифа, технического задания.", default="")
    summary: str = Field(description="Краткое содержание брифа, технического задания.", default="")
    phases: List[ProjectPhase] = Field(description="Этапы работ и задачи для каждого этапа работ.", default_factory=list)
    tasks_with_context: List[ProjectTaskWithContext] = Field(
        description="Этапы работ, задачи для каждого этапа работ и предыдущие знания об оценки и реализации подобных задач.",
        default_factory=list
    )
    estimates: List[Dict[str, List[TaskEstimation]]] = Field(description="Перечень оценок.", default_factory=list)
    excel_file_path: str = Field(description="Путь к Excel файлу, который содержит результат оценки", default="")

    # Служебные
    current_model_index: int = 0 # Индекс текущей модели.
    progress_callback: Optional[Callable] = Field(default=None, exclude=True) # Функция для обновления статуса задачи.
