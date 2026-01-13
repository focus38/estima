from contextlib import asynccontextmanager

from fastapi import FastAPI
from openai import AsyncOpenAI
from starlette.middleware.cors import CORSMiddleware

from backend import config
from backend.ai.workflow import build_estimator_graph
from backend.service.job_manager import EstimatorJobManager

ai_client: AsyncOpenAI | None = None
estimator_graph = None
estimator_job_manager : EstimatorJobManager | None = None

@asynccontextmanager
async def lifespan(application: FastAPI):
    global ai_client
    global estimator_graph
    global estimator_job_manager

    try:
        ai_client = AsyncOpenAI(base_url=config.AI_PROXY_URL, api_key=config.AI_API_KEY)
        estimator_graph = build_estimator_graph()
        estimator_job_manager = EstimatorJobManager()

        from controller.estimator import estimator_router

        application.include_router(estimator_router)
        yield
    finally:
        await ai_client.close()
        del estimator_graph, estimator_job_manager
        print("Resources released.")

app = FastAPI(lifespan=lifespan)

# Эти настройки нужные для локального тестирования
origins = ["http://localhost:8080"]
app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )