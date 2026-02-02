from langgraph.constants import END
from langgraph.graph import StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import RetryPolicy

from backend.ai.nodes.decomposition import decompose
from backend.ai.nodes.estimation import estimate
from backend.ai.nodes.prepare_result import prepare
from backend.ai.nodes.extraction import extract_document_content
from backend.ai.nodes.retrieval import retrieve
from backend.ai.nodes.summarization import summarize
from backend.ai.workflow_state import EstimationState


def should_continue_estimating(state: EstimationState) -> bool:
    if state.current_model_index < len(state.models):
        return True
    else:
        return False

def build_estimator_graph() -> CompiledStateGraph:
    default_retry_policy = RetryPolicy(retry_on=[ConnectionError, TimeoutError], max_attempts=3)
    workflow = StateGraph(EstimationState)
    workflow.add_node("extraction", extract_document_content, retry_policy=default_retry_policy)
    workflow.add_node("summarization", summarize, retry_policy=default_retry_policy)
    workflow.add_node("decomposition", decompose, retry_policy=default_retry_policy)
    workflow.add_node("retrieval", retrieve, retry_policy=default_retry_policy)
    workflow.add_node("estimation", estimate, retry_policy=default_retry_policy)
    workflow.add_node("prepare_result", prepare)

    workflow.set_entry_point("extraction")
    workflow.add_edge("extraction", "summarization")
    workflow.add_edge("summarization", "decomposition")
    workflow.add_edge("decomposition", "retrieval")

    # После retrieval начинаем цикл по моделям
    workflow.add_conditional_edges(
        "retrieval",
        should_continue_estimating,
        {
            True: "estimation",
            False: "prepare_result"
        }
    )

    # После retrieval начинаем цикл по моделям
    workflow.add_conditional_edges(
        "estimation",
        should_continue_estimating,
        {
            True: "estimation",
            False: "prepare_result"
        }
    )

    workflow.add_edge("prepare_result", END)

    return workflow.compile()

estimator_graph: CompiledStateGraph = build_estimator_graph()