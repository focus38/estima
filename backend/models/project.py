from pydantic import BaseModel, Field
from typing import List


class ProjectTaskWithContext(BaseModel):
    phase_name: str = Field(..., description="Наименование этапа работ.")
    task_name: str = Field(..., description="Наименование задачи.")
    context: str = Field(..., description="Контекст задачи.")

class ProjectTask(BaseModel):
    name: str = Field(..., description="Наименование задачи.")
    comment: str = Field(..., description="Комментарий, содержащий особенности или ключевые моменты реализации задачи.")

class ProjectPhase(BaseModel):
    name: str = Field(..., description="Наименование этапа работ.")
    comment: str = Field(..., description="Комментарий, содержащий особенности или ключевые моменты реализации этапа работ.")
    tasks: List[ProjectTask] = Field(..., description="Перечень задач, которые должны быть выполнены в рамках этапа работ.")

    def build_tasks_with_context(self) -> List[ProjectTaskWithContext]:
        result: List[ProjectTaskWithContext] = []
        for t in self.tasks:
            result.append(ProjectTaskWithContext(phase_name=self.name, task_name=t.name, context=""))

        return result