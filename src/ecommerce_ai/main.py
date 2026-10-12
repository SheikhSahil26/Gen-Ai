from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ecommerce_ai.api.router import api_router
from ecommerce_ai.config.settings import settings
from ecommerce_ai.db.database import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # LangChain reads these variables when it creates traces. Settings loads
    # values from .env, while LangSmith itself reads directly from os.environ.
    settings.configure_langsmith()
    try:
        yield
    finally:
        await engine.dispose()


app = FastAPI(
    title="Multi-AI Agentic E-Commerce API",
    description="E-commerce API powered by a multi-agent LangGraph workflow.",
    version="1.0.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)
app.include_router(api_router)


@app.get("/health", tags=["Health"])
@app.get("/api/v1/health", tags=["Health"], include_in_schema=False)
async def health_check():
    return {"status": "ok", "service": "ecommerce-agent-api"}
