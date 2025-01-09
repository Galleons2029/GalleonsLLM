# -*- coding: utf-8 -*-
# @Time    : 2024/9/19 16:54
# @Author  : Galleons
# @File    : chunking.py

"""
由于语言模型有token限制使得输入不能超过这个token限制。
所以当将文本分割成块时，最好先计算token的数量。有很多token标记器。
当计算文本中的token数量时，应该使用与语言模型中相同的token标记器。
文档详见：https://python.langchain.com/docs/how_to/split_by_token/
"""

from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
    SentenceTransformersTokenTextSplitter,
)

from app.config import settings
from app.utils.logging import get_logger
logger = get_logger(__name__)

def chunk_text(text: str) -> list[str]:
    """
    1. 将文本划分为段落
    2. 将字符大于500的段落划分为更小的分块
    3. 保证分块间没有重叠
    :param text: 需要切分的文本
    :return: 包含切分文本分块的列表
    """
    character_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n"],
        chunk_size=500,
        chunk_overlap=0
    )
    text_split = character_splitter.split_text(text)
    logger.debug(f"分段后数据为: {text_split}，现在开始按token切分")

    # # 保证分块符合嵌入模型，并构建小部分重叠
    # token_splitter = SentenceTransformersTokenTextSplitter(
    #     chunk_overlap=50,
    #     tokens_per_chunk=settings.EMBEDDING_MODEL_MAX_INPUT_LENGTH,
    #     model_name=settings.EMBEDDING_MODEL_ID,
    # )
    # chunks = []
    #
    # for section in text_split:
    #     chunks.extend(token_splitter.split_text(section))
    # TODO：查看tiktoken源码改用与嵌入模型适配的token标记器
    retext_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        model_name="gpt-4",
        chunk_size=256,
        chunk_overlap=50,
    )
    chunks = []

    for section in text_split:
        chunks.extend(retext_splitter.split_text(section))

    return chunks
