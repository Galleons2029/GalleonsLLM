# -*- coding: utf-8 -*-
# @Time    : 2025/1/6 15:56
# @Author  : Galleons
# @File    : chat_v4.py

"""
这里是文件说明
"""


import logging
import time
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
# from openai import OpenAI, AsyncOpenAI
import json
from app.config import settings
from app.services.llm.inference_pipeline import InferenceOpenAI
import asyncio

from langfuse.decorators import observe
from langfuse.openai import OpenAI, AsyncOpenAI

# 设置日志配置
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

client = OpenAI(api_key=settings.Silicon_api_key2, base_url=settings.Silicon_base_url)
aclient = AsyncOpenAI(api_key=settings.Silicon_api_key1, base_url=settings.Silicon_base_url)


def story():
    return client.chat.completions.create(
        model="Qwen/Qwen2.5-7B-Instruct",
        max_tokens=1000,
        messages=[
            {"role": "system", "content": "You are a great storyteller."},
            {"role": "user", "content": "请详细介绍一下你自己。"}
        ],
        user_id="开发环境接口测试",
        stream=False,
    ).choices[0].message.content


def main():
    return story()

if __name__ == "__main__":
    main()

    # print(client.chat.completions.create(
    #     model="Qwen/Qwen2.5-7B-Instruct",
    #     max_tokens=1000,
    #     messages=[
    #         {"role": "system", "content": "You are a great storyteller."},
    #         {"role": "user", "content": "请详细介绍一下你自己。"}
    #     ],
    #     stream=False,
    # ).choices[0].message.content)