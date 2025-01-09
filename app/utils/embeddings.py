# -*- coding: utf-8 -*-
# @Time    : 2024/9/18 14:34
# @Author  : Galleons
# @File    : embeddings.py

"""
由于SentenceTransformer以及fastembed的调用都无法保证完全本地读取运行时接口，在调用时延时太长
所以改为调用部署在111服务器上的Xinference模型端口进行嵌入
"""
from app.config import settings

from xinference.client import Client
import numpy as np

client = Client("http://192.168.100.111:9997")
embed_model_raw = client.get_model(settings.EMBEDDING_MODEL_ID)
embed_model = client.get_model(settings.EMBEDDING_MODEL_ID)



def embedd_text(text: str) -> np.ndarray:
    embedding_list = embed_model.create_embedding(text)['data'][0]['embedding']
    return np.array(embedding_list)


def embedd_text_tolist(text: str) -> list[int]:
    embedding_list = embed_model.create_embedding(text)['data'][0]['embedding']
    return embedding_list


# 代码嵌入模型
def embedd_repositories(text: str):
    # TODO：优化代码嵌入模型部分，寻找合适模型
    #model = INSTRUCTOR("hkunlp/instructor-xl")
    #sentence = text
    #instruction = "Represent the structure of the repository"
    #return model.encode([instruction, sentence])
    embedding_list = embed_model.create_embedding(input)['data'][0]['embedding']
    embedding_array = np.array(embedding_list)
    return embedding_array
    #embeddings_generator: np.ndarray = embedding_model.embed(text)
    #embeddings_text = list(embeddings_generator)[0]
    #return embeddings_text


from xinference.client import Client
from tenacity import retry, stop_after_attempt, wait_exponential
from contextlib import contextmanager
from typing import List, Optional, Any, Coroutine
import numpy as np
import logging
from functools import lru_cache
from app.config import settings

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class EmbeddingClientManager:
    _client: Optional[Client] = None
    _embed_model = None

    @classmethod
    @contextmanager
    def get_client_context(cls):
        """获取 Xinference 客户端的上下文管理器"""
        if cls._client is None:
            try:
                cls._client = Client("http://192.168.100.111:9997")
                cls._embed_model = cls._client.get_model("bge-m3")
            except Exception as e:
                logger.error(f"Failed to initialize Xinference client: {str(e)}")
                raise

        try:
            yield cls._embed_model
        except Exception as e:
            logger.error(f"Error during Xinference operation: {str(e)}")
            cls._client = None
            cls._embed_model = None
            raise

    @classmethod
    def check_health(cls) -> bool:
        """检查 Xinference 服务是否可用"""
        try:
            with cls.get_client_context() as embed_model:
                # 尝试进行一个简单的嵌入操作
                test_result = embed_model.create_embedding("test")
                return bool(test_result and test_result.get('data'))
        except Exception as e:
            logger.error(f"Xinference health check failed: {str(e)}")
            return False


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def vectorize(text: str) -> List[float]:
    """
    使用 Xinference 生成文本嵌入向量

    Args:
        text: 需要生成嵌入向量的文本

    Returns:
        List[float]: 嵌入向量

    Raises:
        Exception: 当嵌入生成失败时抛出异常
    """
    if not text:
        return []

    try:
        with EmbeddingClientManager.get_client_context() as embed_model:
            result = embed_model.create_embedding(text)
            if not result or 'data' not in result or not result['data']:
                raise ValueError("Invalid embedding result")

            embedding = result['data'][0]['embedding']
            return embedding

    except Exception as e:
        logger.error(f"Error generating embedding for text: {str(e)}")
        raise


# 可选：为短文本添加缓存以提高性能
@lru_cache(maxsize=1000)
def get_cached_embedding(text: str) -> Coroutine[Any, Any, list[float]]:
    """
    为短文本提供缓存的嵌入向量生成
    仅用于长度小于500字符的文本
    """
    if len(text) > 500:
        return vectorize(text)
    return vectorize(text)