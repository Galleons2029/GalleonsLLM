# -*- coding: utf-8 -*-
# @Time    : 2024/10/16 15:58
# @Author  : Galleons
# @File    : routers.py

"""
RAG知识库平台终端
"""

import logging
from fastapi import FastAPI, Request, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.api.v1.endpoints import (
    knowledge_db, chat_v3, chat_v2
)

# 配置日志格式
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

# api_router = APIRouter()
api_router = FastAPI(
    title="RAG知识库系统",
    summary="文档存储、查询",
    version="1.1.0",
)

api_router.include_router(knowledge_db.router, prefix="/api", tags=["doc-v1"])

api_router.include_router(chat_v3.router, prefix="/v3", tags=["chat-v3"])
api_router.include_router(chat_v2.router, prefix="/v1", tags=["chat-v2"])



@api_router.middleware("http")
async def log_request(request: Request, call_next):
    if request.method == "POST":
        try:
            # 尝试读取和解析请求体
            body = await request.body()
            if body:
                # 如果body不为空,则解码并打印
                body_str = body.decode()
                logging.info(f"收到请求体: {body_str}")
        except Exception as e:
            logging.error(f"读取请求体失败: {str(e)}")

    # 继续处理请求
    response = await call_next(request)
    return response


@api_router.post("/items/")
async def create_item(item: dict):
    return item


@api_router.exception_handler(ValidationError)
async def validation_exception_handler(request, exc: ValidationError):
    error_messages = []
    for error in exc.errors():
        error_messages.append({
            'field': error['loc'][0],
            'message': error['msg'],
            'type': error['type']
        })
    return JSONResponse(
        status_code=422,
        content={'detail': error_messages}
    )


# 添加 CORS 中间件
api_router.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)



if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "routers:api_router",
        host="0.0.0.0",
        port=9011,
        # reload=True,
    )