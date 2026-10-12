import logging
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from langchain_core.messages import HumanMessage
from langgraph.graph.state import CompiledStateGraph

from ecommerce_ai.api.dependencies import get_main_graph
from ecommerce_ai.graph.state import EcommerceState
from ecommerce_ai.schemas.chat import ChatRequest, ChatResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    graph: CompiledStateGraph = Depends(get_main_graph),
) -> ChatResponse:
    conversation_id = request.conversation_id or str(uuid4())
    initial_state: EcommerceState = {
        "messages": [HumanMessage(content=request.message)],
    }

    try:
        result = await graph.ainvoke(
            initial_state,
            config={"configurable": {"thread_id": conversation_id}},
        )
    except Exception as exc:
        logger.exception("Chat graph invocation failed")
        raise HTTPException(
            status_code=502,
            detail="The assistant could not complete this request. Please try again.",
        ) from exc

    messages = result.get("messages", [])
    if not messages or not getattr(messages[-1], "content", None):
        logger.error("Chat graph completed without a final message")
        raise HTTPException(
            status_code=502,
            detail="The assistant returned an empty response. Please try again.",
        )

    return ChatResponse(
        message=messages[-1].content,
        conversation_id=conversation_id,
        intent=(result.get("intents") or [None])[0],
        intent_confidence=result.get("intent_confidence"),
    )
