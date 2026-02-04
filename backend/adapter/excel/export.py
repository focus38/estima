from pathlib import Path
from typing import Any, List, Dict

import pandas as pd

from backend.models.estimation import TaskEstimation
from backend.models.project import ProjectPhase, ProjectTaskWithContext


class ExcelExporter:

    def export(self,
               roles: List[str],
               phases: List[ProjectPhase],
               estimates: List[Dict[str, List[TaskEstimation]]],
               output_path: Path
               ) -> None:
        """
        Экспортирует результаты оценки моделей в Excel файл.

        :param roles: Перечень ролей сотрудников, которые должны участвовать в проекте.
        :param phases: Перечень этапов работ и задач внутри каждого этапа.
        :param estimates: Список словарей вида {model_name: List[TaskEstimation]}.
        :param output_path: Путь к выходному Excel-файлу
        """
        if not roles:
            raise ValueError("Список roles пуст")
        if not phases:
            raise ValueError("Список phases пуст")
        if not estimates:
            raise ValueError("Список estimates пуст")

        # Формируем плоский список всех задач в порядке этапов
        all_tasks: List[ProjectTaskWithContext] = []
        for phase in phases:
            for t in phase.tasks:
                item = ProjectTaskWithContext(
                    phase_name=phase.name,
                    task_name=t.name,
                    context=""
                )
            all_tasks.append(item)

        # 1. Собираем данные по каждой модели
        model_results = {}
        for estimate_dict in estimates:
            model_name, tasks_estimations = next(iter(estimate_dict.items()))
            rows = []
            for i, task in enumerate(all_tasks):
                roles_estimates = self.find_task_by_index(i, tasks_estimations)
                row: Dict[str, Any] = {
                    "Название этапа": task.phase_name,
                    "Название задачи": task.task_name,
                }
                total = 0
                for role in roles:
                    val = self.find_role_estimation(roles_estimates, role)
                    row[role] = val
                    total += val
                row["Итого"] = total
                rows.append(row)
            model_results[model_name] = rows

        # 2. Формируем общий (усреднённый) результат
        overall_rows = []
        for task_item in all_tasks:
            phase_name = task_item.phase_name
            task_name = task_item.task_name
            avg_row: Dict[str, Any] = {
                "Название этапа": phase_name,
                "Название задачи": task_name,
            }
            total_sum = 0
            for role in roles:
                values = [
                    model_rows[i][role]
                    for model_rows in model_results.values()
                    for i, (t) in enumerate(all_tasks)
                    if t.phase_name == phase_name and t.task_name == task_name
                ]
                # TODO Округлить до большего целого числа
                avg_val = round(sum(values) / len(values))
                avg_row[role] = avg_val
                total_sum += avg_val
            avg_row["Итого"] = total_sum
            overall_rows.append(avg_row)

        # 3. Добавляем итоговые строки ко всем таблицам.
        overall_with_total = self.add_total_row(overall_rows, roles)
        model_results_with_total = {
            name: self.add_total_row(rows, roles) for name, rows in model_results.items()
        }

        # 4. Запись в Excel
        with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
            # Первый лист - общий результат.
            df_overall = pd.DataFrame(overall_with_total)
            df_overall.to_excel(writer, sheet_name="Оценка", index=False)

            # Остальные листы - результаты оценки для каждой модели.
            for model_name, rows in model_results_with_total.items():
                # Учитываем ограничение Excel на длину имени листа
                sheet_name = model_name[:31] if len(model_name) <= 31 else model_name[:28] + "..."
                df = pd.DataFrame(rows)
                df.to_excel(writer, sheet_name=sheet_name, index=False)

    @staticmethod
    def find_task_by_index(index: int, estimations: List[TaskEstimation]) -> TaskEstimation | None:
        for item in estimations:
            if item.task_index == index:
                return item
        return None

    @staticmethod
    def find_role_estimation(task_estimation: TaskEstimation | None, role_name: str) -> int:
        if not task_estimation:
            return 0

        if not task_estimation.estimates_by_role:
            return 0
        for item in task_estimation.estimates_by_role:
            if item.role_name == role_name:
                return item.estimate_value
        return 0

    @staticmethod
    def add_total_row(rows: List[Dict], roles: List[str]) -> List[Dict]:
        totals: Dict[str, Any] = {"Название этапа": "Итого", "Название задачи": ""}
        for role in roles:
            totals[role] = sum(row[role] for row in rows)
        totals["Итого"] = sum(totals[role] for role in roles)
        return rows + [totals]