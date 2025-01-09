import concurrent.futures

from app.utils.logging import get_logger
import app.utils
from app.db.qdran import QdrantDatabaseConnector
from qdrant_client import models
from app.services.rag.query_expansion import QueryExpansion
from app.services.rag.reranking import Reranker
from app.services.rag.self_query import SelfQuery
#from sentence_transformers.SentenceTransformer import SentenceTransformer
from app.utils.embeddings import embed_model
from app.config import settings

logger = get_logger(__name__)


class VectorRetriever:
    """
    用于使用查询扩展和多租户搜索从RAG系统中的向量存储中检索向量的类。
    """

    def __init__(self, query: str) -> None:
        self._client = QdrantDatabaseConnector()
        self.query = query
        #self._embedder = SentenceTransformer(settings.EMBEDDING_MODEL_ID)
        self._embedder = embed_model
        self._query_expander = QueryExpansion()
        self._metadata_extractor = SelfQuery()
        self._reranker = Reranker()

    def _search_single_query(
        self, generated_query: str, collections: list[str], metadata_filter_value: dict | None = None, k: int = 3
    ):

        assert k > 3, "查询集合限制，k应该小于3"
        # 生成查询向量
        query_vector = self._embedder.create_embedding(generated_query)['data'][0]['embedding']

        # 初始化存储各集合查询结果的列表
        vectors = []

        # 通用过滤条件
        if metadata_filter_value:
            filter_condition = models.Filter(
                must=[
                    models.FieldCondition(
                        key=metadata_filter_value['key'],
                        match=models.MatchValue(
                            value=metadata_filter_value['value'],
                        ),
                    )
                ]
            )
        else:
            filter_condition = None

        # 遍历集合并进行搜索
        for collection_name in collections:
            # 执行搜索并添加到 vectors 列表中
            vectors.append(
                self._client.search(
                    collection_name=collection_name,
                    query_filter=filter_condition,
                    query_vector=query_vector,
                    limit=k // len(collections),
                )
            )

        return app.utils.flatten(vectors)


    def retrieve_top_k(self,
                       k: int,
                       collections: list[str],
                       filter_setting: dict | None = None,
                       to_expand_to_n_queries: int = 3) -> list:
        # 生成多重查询
        generated_queries = self._query_expander.generate_response(
            self.query, to_expand_to_n=to_expand_to_n_queries
        )
        logger.info(
            "成功生成搜索查询。",
            num_queries=len(generated_queries),
        )

        # 在不同的线程上分别运行各查询以减少网络I/O开销，不受python的GIL限制阻碍
        with concurrent.futures.ThreadPoolExecutor() as executor:
            search_tasks = [
                executor.submit(self._search_single_query, query, collections, filter_setting, k)
                for query in generated_queries
            ]

            hits = [
                task.result() for task in concurrent.futures.as_completed(search_tasks)
            ]   # 等待所有线程
            hits = app.utils.flatten(hits)

        logger.info("成功检索到所有文档。", num_documents=len(hits))

        return hits

    def rerank(self, hits: list, keep_top_k: int) -> list[str]:
        content_list = [hit.payload["content"] for hit in hits]
        rerank_hits = self._reranker.generate_response(
            query=self.query, passages=content_list, keep_top_k=keep_top_k
        )

        logger.info("成功重新排序文档。", num_documents=len(rerank_hits))

        return rerank_hits

    def set_query(self, query: str) -> None:
        self.query = query

