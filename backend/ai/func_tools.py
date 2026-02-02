from typing import List

from openai.types.chat import ChatCompletionFunctionToolParam
from openai.types.shared_params import FunctionDefinition


def create_project_decomposition_tool() -> List[ChatCompletionFunctionToolParam]:
    func_description = """Создаёт структурированное описание этапа проекта, включая его задачи.
    Используется для декомпозиции проекта на этапы работ и конкретные задачи.
    """

    return [ChatCompletionFunctionToolParam(
        type="function",
        function=FunctionDefinition(
            strict=True,
            name="get_project_decomposition",
            description=func_description,
            parameters={
                "type": "object",
                "description": "Результат декомпозиции проекта на этапы работ и задачи внутри этапов.",
                "properties": {
                    "phases": {
                        "type": "array",
                        "description": "Перечень этапов работ, которые должны быть выполнены в рамках проекта.",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "description": "Наименование этапа работ."
                                },
                                "comment": {
                                    "type": "string",
                                    "description": "Комментарий, содержащий особенности или ключевые моменты реализации этапа работ."
                                },
                                "tasks": {
                                    "type": "array",
                                    "description": "Перечень задач, которые должны быть выполнены в рамках этапа работ.",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "name": {
                                                "type": "string",
                                                "description": "Наименование задачи."
                                            },
                                            "comment": {
                                                "type": "string",
                                                "description": "Комментарий, содержащий особенности или ключевые моменты реализации задачи."
                                            }
                                        },
                                        "required": ["name", "comment"],
                                        "additionalProperties": False
                                    }
                                }
                            },
                            "required": ["name", "comment", "tasks"],
                            "additionalProperties": False
                        }
                    }
                },
                "required": ["phases"],
                "additionalProperties": False
            }
        )
    )]

def create_project_estimation_tool(roles: List[str]) -> List[ChatCompletionFunctionToolParam]:
    """
    Создаёт описание функции для оценки задач по ролям.
    Роли передаются, чтобы динамически сформировать схему.
    """
    func_description = "Возвращает оценку трудозатрат по каждой задаче и роли в человеко-часах. Порядок задач должен совпадать с входным списком."
    # Роли для использования в JSON Schema
    role_properties = {
        role: {
            "type": "number",
            "minimum": 0.0,
            "description": f"Оценка трудозатрат для роли '{role}' в человеко-часах"
        }
        for role in roles
    }

    return [ChatCompletionFunctionToolParam(
        type="function",
        function=FunctionDefinition(
            strict=True,
            name="estimate_project_tasks",
            description=func_description,
            parameters={
                "type": "object",
                "properties": {
                    "task_estimations": {
                        "type": "array",
                        "description": "Список оценок по задачам в том же порядке, что и во входных данных.",
                        "items": {
                            "type": "object",
                            "properties": {
                                "task_index": {
                                    "type": "integer",
                                    "minimum": 1,
                                    "description": "Номер задачи (начиная с 1, как в перечне)"
                                },
                                "estimates_by_role": {
                                    "type": "object",
                                    "properties": role_properties,
                                    "required": roles,
                                    "additionalProperties": False
                                }
                            },
                            "required": ["task_index", "estimates_by_role"],
                            "additionalProperties": False
                        }
                    }
                },
                "required": ["task_estimations"],
                "additionalProperties": False
            }
        )
    )]