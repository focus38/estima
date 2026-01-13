from backend.app import estimator_job_manager, estimator_graph
from backend.service.job_manager import EstimatorJobManager


def get_job_manager() -> EstimatorJobManager:
    return estimator_job_manager

def get_estimator_graph():
    return estimator_graph