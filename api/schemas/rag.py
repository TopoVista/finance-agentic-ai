from pydantic import BaseModel, Field


class RagChatInput(BaseModel):
    question: str = Field(min_length=1)


class RagChatResponse(BaseModel):
    answer: str
    sources: list[dict] = []
