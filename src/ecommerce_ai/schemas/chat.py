from pydantic import BaseModel, ConfigDict, Field


class ChatRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="ignore")

    message: str = Field(min_length=1, max_length=5000, description="The user's message.")
    conversation_id: str | None = Field(default=None, min_length=1, max_length=128)


class ChatResponse(BaseModel):
    message: str
    conversation_id: str
    intent: str | None = None
    intent_confidence: float | None = None
    