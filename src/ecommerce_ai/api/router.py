from fastapi import APIRouter

from ecommerce_ai.api.routes.commerce import router as commerce_router
from ecommerce_ai.api.routes.chat import (
    router as chat_router,
)


api_router = APIRouter(
    prefix="/api/v1"
)

api_router.include_router(
    chat_router
)
api_router.include_router(commerce_router)