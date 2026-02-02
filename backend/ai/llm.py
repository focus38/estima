import json
from typing import Any, List

import structlog
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionSystemMessageParam, \
    ChatCompletionUserMessageParam, ChatCompletion

from backend import config
from backend.ai import prompts, func_tools
from backend.models.errors import LLMError
from backend.models.estimation import TaskEstimation, EstimateByRole
from backend.models.project import ProjectPhase, ProjectTaskWithContext

client = AsyncOpenAI(api_key=config.AI_API_KEY, base_url=config.AI_PROXY_URL)
logger = structlog.stdlib.get_logger()

async def summarize_document(text: str) -> str:
    messages: List[ChatCompletionMessageParam] = [
        ChatCompletionSystemMessageParam(
            name="summarize_system_prompt",
            role="system",
            content=prompts.SUMMARIZE_SYSTEM_PROMPT
        ),
        ChatCompletionUserMessageParam(
            name="summarize_user_prompt",
            role="user",
            content=prompts.SUMMARIZE_USER_PROMPT.format(document_content=text)
        )
    ]
    response = await client.chat.completions.create(
        # Небольшая доза вариативности помогает сформулировать мысль естественно,
        # но при этом минимизирует вероятность галлюцинаций и выдумывания.
        temperature=0.2,
        messages=messages,
        timeout=config.AI_API_TIMEOUT,
        model=config.MAIN_MODEL,
        max_tokens=10000
    )
    _validate_llm_response("summarize", response)
    i_tokens, o_tokens, t_tokens = get_usage_tokens(response)
    logger.info(f"Tokens used to to compile a summary of the technical specifications: {i_tokens}, {o_tokens}, {t_tokens}")
    result = response.choices[0].message.content
    return result.strip()

async def decompose_document(text: str, roles: List[str]) -> List[ProjectPhase]:
    roles_str = _create_role_description(roles)
    messages: List[ChatCompletionMessageParam] = [
        ChatCompletionSystemMessageParam(
            name="decompose_system_prompt",
            role="system",
            content=prompts.DECOMPOSE_SYSTEM_PROMPT
        ),
        ChatCompletionUserMessageParam(
            name="decompose_user_prompt",
            role="user",
            content=prompts.DECOMPOSE_USER_PROMPT.format(document_content=text, roles=roles_str)
        )
    ]
    decompose_tools = func_tools.create_project_decomposition_tool()
    response = await client.chat.completions.create(
        temperature=0.1,
        tools=decompose_tools,
        tool_choice="required",
        messages=messages,
        timeout=config.AI_API_TIMEOUT,
        parallel_tool_calls=False,
        model=config.MAIN_MODEL,
        verbosity="medium",
        reasoning_effort="minimal",
        max_tokens=10000
    )

    _validate_llm_response("decompose", response)
    i_tokens, o_tokens, t_tokens = get_usage_tokens(response)
    logger.info(f"Tokens used to decompose project into stages and tasks: {i_tokens}, {o_tokens}, {t_tokens}")

    message = response.choices[0].message
    answer = message.tool_calls[0].function.arguments
    try:
        decomposition = json.loads(answer)
    except json.JSONDecodeError as e:
        error_msg = "Невозможно распознать function.arguments как JSON"
        logger.error(f"{error_msg}: {e}\nRaw: {answer}")
        raise LLMError(stage="decompose", message=error_msg)

    raw_phases = decomposition.get("phases", [])
    if not isinstance(raw_phases, list):
        error_msg = f"Ожидался список этапов (list), но получен тип: {type(raw_phases)}"
        logger.error(error_msg)
        raise LLMError(stage="decompose", message=error_msg)

    return [ProjectPhase.model_validate(phase) for phase in raw_phases]

async def estimate(
        model: str,
        summary: str,
        tasks: List[ProjectTaskWithContext],
        roles: List[str]
) -> List[TaskEstimation]:
    roles_str = _create_role_description(roles)
    tasks_str = _create_task_description(tasks)
    user_prompt = prompts.ESTIMATE_USER_PROMPT.format(
        document_summary=summary,
        roles=roles_str,
        tasks=tasks_str
    )
    messages: List[ChatCompletionMessageParam] = [
        ChatCompletionSystemMessageParam(
            name="estimate_system_prompt",
            role="system",
            content=prompts.ESTIMATE_SYSTEM_PROMPT
        ),
        ChatCompletionUserMessageParam(
            name="estimate_user_prompt",
            role="user",
            content=user_prompt
        )
    ]
    estimate_tools = func_tools.create_project_estimation_tool(roles)
    response = await client.chat.completions.create(
        temperature=0.1,
        tools=estimate_tools,
        tool_choice="required",
        messages=messages,
        timeout=config.AI_API_TIMEOUT,
        parallel_tool_calls=False,
        model=model,
        verbosity="medium",
        reasoning_effort="minimal",
        max_tokens=10000
    )
    _validate_llm_response("estimate", response)
    i_tokens, o_tokens, t_tokens = get_usage_tokens(response)
    logger.info(f"Tokens used for estimate tasks: {i_tokens}, {o_tokens}, {t_tokens}")

    message = response.choices[0].message
    answer = message.tool_calls[0].function.arguments
    try:
        result = json.loads(answer)
    except json.JSONDecodeError as e:
        error_msg = "Невозможно распознать function.arguments как JSON"
        logger.error(f"{error_msg}: {e}\nRaw: {answer}")
        raise LLMError(stage="decompose", message=error_msg)

    if not isinstance(result, dict):
        error_msg = f"Ожидался объект (dict), но получен тип: {type(result)}"
        logger.error(error_msg)
        raise LLMError(stage="decompose", message=error_msg)

    task_estimations_raw = result.get("task_estimations", [])
    try:
        return  _create_tasks_estimations(task_estimations_raw)
    except Exception as e:
        logger.error(f"Ошибка валидации оценки: {e}")
        raise LLMError(stage="estimate", message="Некорректный формат оценки от LLM")

def get_usage_tokens(completion: ChatCompletion) -> tuple[int, int, int]:
    input_tokens = completion.usage.prompt_tokens if completion.usage is not None else 0
    output_tokens = completion.usage.completion_tokens if completion.usage is not None else 0
    total_tokens = completion.usage.total_tokens if completion.usage is not None else 0
    return input_tokens, output_tokens, total_tokens

def _create_role_description(roles: List[str]) -> str:
    lines: List[str] = []
    for idx, role in enumerate(roles, start=1):
        lines.append(f"\n{idx}. '{role}'")
    return "\n".join(lines)

def _create_task_description(tasks: List[ProjectTaskWithContext]) -> str:
    lines = ["Перечень задач для оценки (сохраняй порядок и нумерацию при ответе):"]
    for idx, task in enumerate(tasks, start=1):
        phase_name = task.phase_name.strip() if task.phase_name else ""
        task_name = task.task_name.strip() if task.task_name else ""
        context = task.context.strip() if task.context else ""

        lines.append(f"\n{idx}. Этап: {phase_name}")
        lines.append(f"   Задача: {task_name}")
        if context:
            lines.append(f"   Контекст: {context}")
    return "\n".join(lines)

def _validate_llm_response(stage: str, response: ChatCompletion) -> None:
    if not response:
        error_msg = "Получен пустой ответ от LLM API."
        logger.error(error_msg)
        raise LLMError(stage=stage, message=error_msg)

    if not hasattr(response, 'choices') or not response.choices:
        error_msg = "В ответе отсутствует поле 'choices' или оно пустое."
        logger.error(error_msg)
        raise LLMError(stage=stage, message=error_msg)

    if not response.choices[0].message:
        error_msg = "Первый choice не содержит message."
        logger.error(error_msg)
        raise LLMError(stage=stage, message=error_msg)

def _create_tasks_estimations(estimates: List[Any]) -> List[TaskEstimation]:
    result: List[TaskEstimation] = []
    for item in estimates:
        task_index = item.get("task_index", 0)
        estimates_by_role_raw = item.get("estimates_by_role", {})
        estimates_by_role: List[EstimateByRole] = []
        for role_name in estimates_by_role_raw:
            estimate_value = estimates_by_role_raw[role_name]
            estimates_by_role.append(EstimateByRole(role_name=role_name, estimate_value=estimate_value))

        task_estimations = TaskEstimation(task_index=task_index, estimates_by_role=estimates_by_role)
        result.append(task_estimations)

    return result