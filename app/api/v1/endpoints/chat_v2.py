# -*- coding: utf-8 -*-
# @Time    : 2025/1/3 15:05
# @Author  : Galleons
# @File    : chat_v2.py

"""
流式输出API
"""

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
# from openai import OpenAI
from langfuse.openai import OpenAI, AsyncOpenAI
import json
from app.config import settings
from app.services.llm.inference_pipeline import InferenceOpenAI


router = APIRouter()

client = OpenAI(api_key=settings.Silicon_api_key2, base_url=settings.Silicon_base_url)


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[Message]
    model: str = "Qwen/Qwen2.5-72B-Instruct"
    collections: List[str]
    temperature: Optional[float] = 1.0
    stream: bool = True
    max_tokens: Optional[int] = None
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "messages": [
                    {
                        "role": "user",
                        "content": "You are a helpful assistant."
                    }
                ],
                "model": "qwen2-pro",
                "collections": ["zsk_1"],
                "temperature": 1,
                "stream": True,
            }
        })


async def generate_stream(messages: List[Message], model: str, temperature: float):
    response = client.chat.completions.create(
        messages=[{"role": message.role, "content": message.content} for message in messages],
        model="Qwen/Qwen2.5-72B-Instruct",
        temperature=temperature,
        stream=True,
        user_id='v2_rag测试接口',
    )

    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            # 构造与OpenAI格式一致的响应
            response_data = {
                "id": "chatcmpl-" + chunk.id,
                "object": "chat.completion.chunk",
                "created": chunk.created,
                "model": model,
                "choices": [
                    {
                        "index": chunk.id,
                        "delta": {
                            "content": chunk.choices[0].delta.content
                        },
                        "finish_reason": chunk.choices[0].finish_reason
                    }
                ]
            }
            yield f"data: {json.dumps(response_data)}\n\n"

    yield "data: [DONE]\n\n"


@router.post("/chat/completions/stream")
async def chat_stream(request: ChatRequest):
    llm = InferenceOpenAI()
    request.messages[-1].content = llm.generate(
        query=request.messages[-1].content,
        collections=request.collections,
        enable_rag=True,
    )

    return StreamingResponse(
        generate_stream(
            messages=request.messages,
            model=request.model,
            temperature=request.temperature
        ),
        media_type="text/event-stream"
    )
