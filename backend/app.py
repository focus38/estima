import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from openai import AsyncOpenAI
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import FileResponse
from starlette.staticfiles import StaticFiles

from backend import config
from backend.utils.log_utils import configure_logger, get_logger

ai_client: AsyncOpenAI | None = None

configure_logger(enable_json_logs=True)
# Дополнительно настройка для starlette
logging.getLogger("starlette.error").setLevel(logging.WARNING)

logger = get_logger()

@asynccontextmanager
async def lifespan(application: FastAPI):
    global ai_client

    try:
        ai_client = AsyncOpenAI(base_url=config.AI_PROXY_URL, api_key=config.AI_API_KEY)

        from backend.controller.job import job_router
        from backend.controller.role import role_router
        from backend.controller.estimator import estimator_router

        application.include_router(job_router)
        application.include_router(role_router)
        application.include_router(estimator_router)
        yield
    finally:
        await ai_client.close()
        del ai_client
        logger.info("Resources released.")

app = FastAPI(lifespan=lifespan)
app.logger = logger

# Монтируем статические файлы
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Маршрут для главной страницы
@app.get("/")
async def read_index():
    return FileResponse("frontend/index.html")

# Эти настройки нужные для локального тестирования
origins = ["http://localhost:8080"]
app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )