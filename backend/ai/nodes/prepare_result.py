import asyncio
import logging
from pathlib import Path

from backend import config
from backend.adapter.excel.export import ExcelExporter
from backend.ai.workflow_state import EstimationState
from backend.models.errors import JobError
from backend.models.job import EstimationStage


logger = logging.getLogger(__name__)

async def prepare(state: EstimationState) -> EstimationState:
    logger.info("Started formalizing the estimation results.")
    if state.progress_callback:
        await asyncio.to_thread(state.progress_callback, state.job_id, EstimationStage.PREPARE_RESULT, None)

    try:
        filename = f"estima_result_{state.job_id}.xlsx"
        export_path = config.RESULTS_DIR / filename
        export_path.parent.mkdir(parents=True, exist_ok=True)
        excel_exporter = ExcelExporter()
        excel_exporter.export(state.roles, state.phases, state.estimates, export_path)
        state.excel_file_path = str(export_path)
        logger.info("Finished formalizing the evaluation results.")
        return state
    except Exception as ex:
        logger.error("Error in the process of forming the estimation results.", exc_info=ex)
        raise JobError("prepare_result", "Error in the process of forming the estimation results.")
