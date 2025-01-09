# -*- coding: utf-8 -*-
# @Time    : 2025/1/6 16:57
# @Author  : Galleons
# @File    : langchain_rag.py

"""
Langchain RAG 测试接口
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
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough



system_prompt = """
The following is a conversation with an AI assistant. 
The assistant is helpful, creative, clever, and very friendly.\n\n
Human: Hello, who are you?\n
AI: I am an AI created by OpenAI. How can I help you today?
\nHuman: 
"""

class Prompt(BaseModel):
    message: str
@router.post("/prompt/stream")
async def prompt_response_stream(prompt: Prompt):
    openai_response = await aclient.chat.completions.create(
        model="Qwen/Qwen2.5-7B-Instruct",
        stream=True,
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt.message},
                ],
            }
        ],
    )

    async def generate():
        async for token in openai_response:
            content = token.choices[0].delta.content
            if content is not None:
                yield content

    return StreamingResponse(generate(), media_type="text/event-stream")




from langfuse.callback import CallbackHandler
langfuse_handler = CallbackHandler(
    public_key="pk-lf-a80b5716-aecb-4132-bc7d-3c7a2943708b",
    secret_key="sk-lf-d536cdbc-c64b-41db-a6d1-cf098614bc39",
    host="http://localhost:3000"
)

template = """基于以下信息回答下列问题：
{context}

问题：{question}
"""

async def generate_chat_responses(message):
    llm = InferenceOpenAI()
    # prompt = ChatPromptTemplate.from_template(template)
    model = ChatOpenAI(
        model=settings.Silicon_model_v1,
        openai_api_key=settings.Silicon_api_key1,
        openai_api_base=settings.Silicon_base_url,
    )

    prompt = ChatPromptTemplate.from_template("tell me a joke about {topic}")
    parser = StrOutputParser()
    chain = prompt | model | parser

    for chunk in chain.stream({"topic": "parrot"}):
        print(chunk, end="|", flush=True)

    retrieval_chain = (
            {
                "context": llm.generate(
                    query=message,
                    collections=['zsk_1'],
                    enable_rag=True,
                ),
                "question": RunnablePassthrough(),
            }
            | prompt
            | model
            | StrOutputParser()
    )

    async for chunk in retrieval_chain.astream(message, config={"callbacks": [langfuse_handler]}):
        content = chunk.replace("\n", "<br>")
        yield f"data: {content}\n\n"

@router.post("/chat/completions/v3")
async def chat_stream(request: ChatRequest):
    return StreamingResponse(generate_chat_responses(message=request.messages[-1].content), media_type="text/event-stream")


