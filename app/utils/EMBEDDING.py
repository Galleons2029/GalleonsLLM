# -*- coding: utf-8 -*-
# @Time    : 2024/11/9 19:42
# @Author  : Galleons
# @File    : EMBEDDING.py

"""
这里是文件说明
"""
from typing import List, Dict, Union, Optional, Tuple
import logging
from functools import lru_cache
from FlagEmbedding import BGEM3FlagModel
import torch
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import time

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EmbeddingServiceError(Exception):
    """自定义嵌入服务错误类"""
    pass


class BGEM3EmbeddingService:
    def __init__(
            self,
            model_name: str = 'BAAI/bge-m3',
            use_fp16: bool = True,
            max_workers: int = 4,
            cache_size: int = 1024,
            batch_size: int = 32
    ):
        """
        初始化 BGE M3 嵌入服务

        Args:
            model_name: 模型名称或路径
            use_fp16: 是否使用半精度
            max_workers: 最大线程数
            cache_size: LRU缓存大小
            batch_size: 批处理大小
        """
        try:
            self.model = BGEM3FlagModel(model_name, use_fp16=use_fp16)
            self.executor = ThreadPoolExecutor(max_workers=max_workers)
            self.batch_size = batch_size
            logger.info(f"Successfully initialized BGE M3 model: {model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize model: {str(e)}")
            raise EmbeddingServiceError(f"Model initialization failed: {str(e)}")

    @lru_cache(maxsize=1024)
    def _get_cached_embedding(self, text: str) -> dict:
        """
        获取文本嵌入的缓存实现

        Args:
            text: 输入文本

        Returns:
            包含dense和sparse嵌入的字典
        """
        return self.get_embedding([text])[0]

    def _validate_input(self, texts: List[str]) -> None:
        """
        验证输入文本

        Args:
            texts: 输入文本列表

        Raises:
            EmbeddingServiceError: 当输入无效时
        """
        if not texts:
            raise EmbeddingServiceError("Input texts cannot be empty")
        if not all(isinstance(t, str) for t in texts):
            raise EmbeddingServiceError("All inputs must be strings")
        if any(not t.strip() for t in texts):
            raise EmbeddingServiceError("Empty strings are not allowed")

    def get_embedding(
            self,
            texts: List[str],
            return_dense: bool = True,
            return_sparse: bool = True,
            return_colbert_vecs: bool = False,
            batch_size: Optional[int] = None
    ) -> List[Dict[str, Union[np.ndarray, Dict[str, float]]]]:
        """
        获取文本嵌入

        Args:
            texts: 输入文本列表
            return_dense: 是否返回密集向量
            return_sparse: 是否返回稀疏向量
            return_colbert_vecs: 是否返回ColBERT向量
            batch_size: 批处理大小，None时使用默认值

        Returns:
            包含请求嵌入类型的字典列表

        Raises:
            EmbeddingServiceError: 处理过程中发生错误时
        """
        try:
            # 输入验证
            self._validate_input(texts)

            # 使用指定的batch_size或默认值
            actual_batch_size = batch_size or self.batch_size

            # 记录开始时间
            start_time = time.time()

            # 批处理编码
            outputs = []
            for i in range(0, len(texts), actual_batch_size):
                batch_texts = texts[i:i + actual_batch_size]
                batch_output = self.model.encode(
                    batch_texts,
                    return_dense=return_dense,
                    return_sparse=return_sparse,
                    return_colbert_vecs=return_colbert_vecs
                )
                outputs.extend(self._process_batch_output(batch_output))

            # 记录处理时间
            processing_time = time.time() - start_time
            logger.info(f"Processed {len(texts)} texts in {processing_time:.2f} seconds")

            return outputs

        except Exception as e:
            logger.error(f"Error during embedding generation: {str(e)}")
            raise EmbeddingServiceError(f"Failed to generate embeddings: {str(e)}")

    def _process_batch_output(self, batch_output: dict) -> List[dict]:
        """
        处理批处理输出

        Args:
            batch_output: 模型的原始输出

        Returns:
            处理后的输出列表
        """
        processed_outputs = []

        if isinstance(batch_output, dict):
            num_samples = len(batch_output.get('dense_vecs', [])) if 'dense_vecs' in batch_output else len(
                batch_output.get('lexical_weights', []))

            for i in range(num_samples):
                sample_output = {}
                if 'dense_vecs' in batch_output:
                    sample_output['dense_vecs'] = batch_output['dense_vecs'][i]
                if 'lexical_weights' in batch_output:
                    sample_output['lexical_weights'] = batch_output['lexical_weights'][i]
                if 'colbert_vecs' in batch_output:
                    sample_output['colbert_vecs'] = batch_output['colbert_vecs'][i]
                processed_outputs.append(sample_output)

        return processed_outputs

    def compute_similarity(
            self,
            text1: str,
            text2: str,
            use_lexical: bool = True,
            use_dense: bool = True
    ) -> Dict[str, float]:
        """
        计算两个文本之间的相似度

        Args:
            text1: 第一个文本
            text2: 第二个文本
            use_lexical: 是否使用词法匹配分数
            use_dense: 是否使用密集向量相似度

        Returns:
            包含各种相似度分数的字典
        """
        try:
            # 获取嵌入
            embedding1 = self._get_cached_embedding(text1)
            embedding2 = self._get_cached_embedding(text2)

            scores = {}

            # 计算词法匹配分数
            if use_lexical and 'lexical_weights' in embedding1 and 'lexical_weights' in embedding2:
                lexical_score = self.model.compute_lexical_matching_score(
                    embedding1['lexical_weights'],
                    embedding2['lexical_weights']
                )
                scores['lexical_score'] = float(lexical_score)

            # 计算密集向量相似度
            if use_dense and 'dense_vecs' in embedding1 and 'dense_vecs' in embedding2:
                dense_score = torch.nn.functional.cosine_similarity(
                    torch.tensor(embedding1['dense_vecs']).unsqueeze(0),
                    torch.tensor(embedding2['dense_vecs']).unsqueeze(0)
                ).item()
                scores['dense_score'] = float(dense_score)

            # 计算组合分数
            if use_lexical and use_dense and len(scores) == 2:
                scores['combined_score'] = (scores['lexical_score'] + scores['dense_score']) / 2

            return scores

        except Exception as e:
            logger.error(f"Error computing similarity: {str(e)}")
            raise EmbeddingServiceError(f"Failed to compute similarity: {str(e)}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.executor.shutdown()


# 使用示例
if __name__ == "__main__":
    # 创建服务实例
    service = BGEM3EmbeddingService()

    # 示例文本
    texts = [
        "What is BGE M3?",
        "Defination of BM25",
        "BGE M3 is an embedding model supporting dense retrieval."
    ]

    # 获取嵌入
    embeddings = service.get_embedding(texts)
    print(f"Generated embeddings for {len(texts)} texts")

    # 计算相似度
    similarity = service.compute_similarity(texts[0], texts[2])
    print(f"Similarity scores: {similarity}")
