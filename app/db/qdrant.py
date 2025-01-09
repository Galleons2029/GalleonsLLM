# -*- coding: utf-8 -*-
# @Time    : 2024/11/8 15:54
# @Author  : Galleons
# @File    : qdrant.py

"""
这里是文件说明
"""

# utils/qdrant_client.py
import logging
from typing import Optional
from contextlib import contextmanager
from qdrant_client import QdrantClient, models
from pydantic import BaseModel
import os
from app.config import get_qdrant_settings

logger = logging.getLogger(__name__)


class QdrantSettings(BaseModel):
    # Only include the required fields for Qdrant connection
    url: str
    api_key: str | None = None
    port: int | None = None
    
    class Config:
        extra = "forbid"  # This prevents extra fields from being accepted


class QdrantClientManager:
    _instance: Optional[QdrantClient] = None

    @classmethod
    def get_client(cls) -> QdrantClient:
        """
        获取Qdrant客户端单例实例
        """
        if cls._instance is None:
            settings = QdrantSettings(
                url=os.getenv("QDRANT_URL", "http://192.168.100.146:6333"),
                # api_key=os.getenv("QDRANT_API_KEY"),
                port=None,
            )
            try:
                cls._instance = QdrantClient(
                    url=settings.url,
                    # api_key=settings.api_key
                    port=settings.port,
                )
                logger.info("成功初始化 Qdrant 客户端连接")
            except Exception as e:
                logger.error(f"初始化 Qdrant 客户端失败: {str(e)}")
                raise
        return cls._instance

    @classmethod
    def check_health(cls) -> bool:
        """
        检查Qdrant服务健康状态
        """
        try:
            client = cls.get_client()
            client.get_collections()
            return True
        except Exception as e:
            logger.error(f"Qdrant 健康检查失败: {str(e)}")
            return False

    @classmethod
    @contextmanager
    def get_client_context(cls):
        """
        提供上下文管理器方式使用客户端
        """
        client = None
        try:
            client = cls.get_client()
            yield client
        except Exception as e:
            logger.error(f"使用 Qdrant 客户端时发生错误: {str(e)}")
            raise
        finally:
            if client:
                # 这里可以添加任何需要的清理操作
                pass




