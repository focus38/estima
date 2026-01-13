from typing import Dict, List, Optional

from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.graph.state import CompiledStateGraph
from pydantic import BaseModel, Field


class EstimationState(BaseModel):
    text: str = Field(description="Текст брифа, технического задания.", default="")
    settings: Dict = Field(description="Дополнительные настройки", default_factory=dict)
    summary: str = Field(description="Краткое содержание брифа, технического задания.", default="")
    phases: List[Dict] = Field(description="Этапы работ и задачи для каждого этапа работ.", default_factory=list)
    roles: List[str] = Field(description="Роли участников для реализации задания.", default_factory=list)
    tasks_with_context: List[Dict] = Field(
        description="Этапы работ, задачи для каждого этапа работ и предыдущие знания об оценки и реализации подобных задач.",
        default_factory=list
    )
    estimates: List[Dict] = Field(description="Перечень оценок.", default_factory=list)
    #progress_callback: Optional[callable]

async def start(state: EstimationState):
    return {}

async def end(state: EstimationState):
    return {}

def build_estimator_graph() -> CompiledStateGraph:
    workflow = StateGraph(EstimationState)
    workflow.add_node("start", start)
    workflow.add_node("end", end)
    workflow.set_entry_point("start")
    workflow.add_edge("start", "end")
    workflow.add_edge("end", END)
#    workflow.add_node("summarize", summarize_node)
#    workflow.add_node("extract", extract_phases_node)
#    workflow.add_node("rag", rag_node)
#    workflow.add_node("estimate", estimate_node)
#
#    workflow.set_entry_point("summarize")
#    workflow.add_edge("summarize", "extract")
#    workflow.add_edge("extract", "rag")
#    workflow.add_edge("rag", "estimate")
#    workflow.add_edge("estimate", END)
#
    return workflow.compile()