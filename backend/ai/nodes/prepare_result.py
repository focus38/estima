import asyncio
from pathlib import Path

from backend.adapter.excel.export import ExcelExporter
from backend.ai.workflow_state import EstimationState
from backend.models.job import EstimationStage


async def prepare(state: EstimationState) -> EstimationState:
    if state.progress_callback:
        await asyncio.to_thread(state.progress_callback, state.job_id, EstimationStage.PREPARE_RESULT, None)

    filename = f"estima_result_{state.job_id}.xlsx"
    export_path = Path("data/results") / filename
    export_path.parent.mkdir(parents=True, exist_ok=True)
    excel_exporter = ExcelExporter()
    excel_exporter.export(state.roles, state.phases, state.estimates, export_path)
    state.excel_file_path = str(export_path)

    return state
