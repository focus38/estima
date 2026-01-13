from pathlib import Path
from typing import Callable, Dict
from uuid import UUID

from langgraph.graph.state import CompiledStateGraph

from backend.ai.workflow import EstimationState
from backend.models.job import JobStatus


async def process_job(
        estimator_graph: CompiledStateGraph,
        job_id: UUID,
        file_path: str,
        settings: Dict,
        update_status: Callable[[UUID, JobStatus, float, str | None], None]
):
    # 1. Извлечение текста
    update_status(job_id, JobStatus.extracting, 15.0, None)
    #text = extract_text(file_path)
    text = ""

    update_status(job_id, JobStatus.summarizing, 30.0, None)
    state = EstimationState(
        text=text,
        settings=settings,
        #progress_callback=lambda id, p, s, e: update_status(id, s, p, e)
    )
    result = await estimator_graph.ainvoke(
        input=state
    )

    update_status(job_id, JobStatus.exporting, 90.0, None)
    filename = f"estima_result_{job_id}.xlsx"
    export_path = Path("data/results") / filename
    export_path.parent.mkdir(parents=True, exist_ok=True)
    #export_to_excel(result, export_path)

    update_status(job_id, JobStatus.done, 100.0, None)
    return {
        "job_id": job_id,
        "summary": result["summary"],
        "phases": result["phases"],
        "estimates": result["estimates"],
        "excel_url": f"/download/{filename}"
    }
