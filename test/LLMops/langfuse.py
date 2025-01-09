# -*- coding: utf-8 -*-
# @Time    : 2025/1/6 15:50
# @Author  : Galleons
# @File    : langfuse.py

"""
这里是文件说明
"""

from langfuse.decorators import observe
from langfuse.openai import OpenAI, AsyncOpenAI, openai

LANGFUSE_SECRET_KEY='sk-lf-9ef72003-b1d7-42b7-9ad5-0d6ea7b3b3bc'
LANGFUSE_PUBLIC_KEY='pk-lf-333f2b59-55e4-4299-95e9-0c25417d3db6'
LANGFUSE_HOST="http://localhost:3000"


@observe()
def story():
    return openai.chat.completions.create(
        model="Qwen/Qwen2.5-7B-Instruct",
        max_tokens=100,
        messages=[
            {"role": "system", "content": "You are a great storyteller."},
            {"role": "user", "content": "Once upon a time in a galaxy far, far away..."}
        ],
    ).choices[0].message.content


@observe()
def main():
    return story()


main()