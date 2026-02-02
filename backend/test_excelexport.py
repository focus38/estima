import pickle
from pathlib import Path

from backend.adapter.excel.export import ExcelExporter
from backend.ai.workflow_state import EstimationState

state = EstimationState(file_path="../../data/uploads/2c68254c-a0b6-455d-aa2f-1d54a36f7ef1_1.docx")
with open('../../state.roles.pkl', 'rb') as file:
    state.roles = pickle.load(file)

with open('../../state.phases.pkl', 'rb') as file:
    state.phases = pickle.load(file)

with open('../../state.estimates.pkl', 'rb') as file:
    state.estimates = pickle.load(file)

filename = f"estima_result_{state.job_id}.xlsx"
export_path = Path("../data/results") / filename
export_path.parent.mkdir(parents=True, exist_ok=True)
excel_exporter = ExcelExporter()
excel_exporter.export(state.roles, state.phases, state.estimates, export_path)
state.excel_file_path = str(export_path)