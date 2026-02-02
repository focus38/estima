from pydantic import BaseModel, Field
from typing import List


class EstimateByRole(BaseModel):
    role_name: str = Field(description="Название роли", default="")
    estimate_value: int = Field(description=f"Оценка для роли в человеко-часах")

    class Config:
        extra = "forbid"

class TaskEstimation(BaseModel):
    task_index: int = Field(ge=0, description="Номер задачи (начиная с 1)")
    estimates_by_role: List[EstimateByRole]

    class Config:
        extra = "forbid"
