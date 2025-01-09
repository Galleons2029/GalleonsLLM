# -*- coding: utf-8 -*-
# @Time    : 2024/10/24 14:46
# @Author  : Galleons
# @File    : chat_v3.py
"""
流式输出API
"""

import logging
import time
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
# from openai import OpenAI, AsyncOpenAI
from langfuse.openai import OpenAI, AsyncOpenAI
import json
from app.config import settings
from app.services.llm.inference_pipeline import InferenceOpenAI
import asyncio



# 设置日志配置
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

client = OpenAI(api_key=settings.Silicon_api_key2, base_url=settings.Silicon_base_url)
aclient = AsyncOpenAI(api_key=settings.Silicon_api_key1, base_url=settings.Silicon_base_url)

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
    start_time = time.time()
    logger.info("开始生成流式响应")
    
    logger.info("创建聊天补全请求...")
    response = await aclient.chat.completions.create(
        messages=[{"role": message.role, "content": message.content} for message in messages],
        model="Qwen/Qwen2.5-72B-Instruct",
        temperature=temperature,
        stream=True,
        user_id='v3异步RAG测试接口'
    )
    logger.info(f"聊天补全请求创建完成，耗时：{time.time() - start_time:.2f} 秒")

    async def async_generator():
        chunk_start_time = time.time()
        chunk_count = 0
        try:
            async for chunk in response:
                if chunk_count == 0:
                    logger.info(f"首个数据块接收时间：{time.time() - chunk_start_time:.2f} 秒")
                
                if chunk.choices[0].delta.content is not None:
                    response_data = {
                        "id": "chatcmpl-" + chunk.id,
                        "object": "chat.completion.chunk",
                        "created": chunk.created,
                        "model": model,
                        "choices": [
                            {
                                "index": chunk.choices[0].index,
                                "delta": {
                                    "content": chunk.choices[0].delta.content
                                },
                                "finish_reason": chunk.choices[0].finish_reason
                            }
                        ]
                    }
                    chunk_count += 1
                    # 添加 flush 标志确保立即发送
                    if chunk_count % 1 == 0:  # 每个chunk都立即发送
                        logger.debug(f"发送第 {chunk_count} 个数据块")
                        yield f"data: {json.dumps(response_data)}\n\n"
                        await asyncio.sleep(0)  # 让出控制权，确保数据能够被发送
            
            logger.info(f"处理的数据块总数：{chunk_count}")
            logger.info(f"流式传输总耗时：{time.time() - chunk_start_time:.2f} 秒")
            yield "data: [DONE]\n\n"
        except Exception as e:
            logger.error(f"生成器中发生错误：{str(e)}")
            error_response = {"error": str(e)}
            yield f"data: {json.dumps(error_response)}\n\n"
            yield "data: [DONE]\n\n"

    # 使用自定义的 StreamingResponse 配置
    return StreamingResponse(
        async_generator(),
        media_type="text/event-stream",
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no',  # 禁用 Nginx 缓冲
        }
    )

@router.post("/chat/completions/stream")
async def chat_stream(request: ChatRequest):
    start_time = time.time()
    logger.info("开始处理聊天流式请求")
    
    logger.info("初始化 InferenceOpenAI...")
    llm = InferenceOpenAI()
    logger.info(f"InferenceOpenAI 初始化完成，耗时：{time.time() - start_time:.2f} 秒")
    
    logger.info("使用 RAG 生成内容...")
    rag_start_time = time.time()
    request.messages[-1].content = llm.generate(
        query=request.messages[-1].content,
        collections=request.collections,
        enable_rag=True,
    )
    logger.info(f"RAG 内容生成完成，耗时：{time.time() - rag_start_time:.2f} 秒")

    logger.info("开始生成流式响应...")
    stream_start_time = time.time()
    response = await generate_stream(
        messages=request.messages,
        model=request.model,
        temperature=request.temperature
    )
    logger.info(f"流式生成完成，耗时：{time.time() - stream_start_time:.2f} 秒")
    logger.info(f"接口总耗时：{time.time() - start_time:.2f} 秒")
    
    return response
