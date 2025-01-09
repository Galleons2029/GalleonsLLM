# -*- coding: utf-8 -*-
# @Time    : 2024/11/8 15:59
# @Author  : Galleons
# @File    : by_qdrant.py

"""
注入Qdrant客户端
"""


# dependencies/qdrant.py
from fastapi import Depends, HTTPException, status
from app.db.qdrant import QdrantClientManager
from qdrant_client import QdrantClient


async def get_qdrant_client() -> QdrantClient:
    """
    FastAPI依赖项，用于在路由中获取Qdrant客户端
    """
    if not QdrantClientManager.check_health():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Qdrant service is not available"
        )
    return QdrantClientManager.get_client()