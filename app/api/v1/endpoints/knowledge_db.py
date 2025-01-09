# -*- coding: utf-8 -*-
# @Time    : 2024/12/27 11:08
# @Author  : Galleons
# @File    : knowledge_db.py

"""
这里是文件说明
"""

from fastapi import APIRouter, Body, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from typing import List, Dict, Optional
import random
import logging

router = APIRouter()


class Table(BaseModel):
    query: str
    collections: List[str] = Field(default_factory=list)
    enable_rag: bool = Field(default=True)
    enable_evaluation: bool = False
    enable_monitoring: bool = False



# @router.post(
#     "/query/",
#     response_description="知识库查询",
#     status_code=status.HTTP_201_CREATED,
#     response_model_by_alias=False,
# )
# async def predict(messages: Table = Body(...)):
#     """
#     RAG知识库查询。
#
#     根据选定的集合进行向量库检索。
#     """
#
#     return messages


stored_posts = [
    {"id":"1", "author": "Max", "body": "This is my first post"},
    {"id":"2", "author": "Manuel", "body": "This is another post"}
]

# 创建数据模型
class Post(BaseModel):
    id: str
    author: str
    body: str

# 路由：获取所有帖子
@router.get("/posts")
async def get_posts():
    """
    获取所有帖子
    """
    logging.info("Received request to get all posts")
    return {"posts": stored_posts}

# 路由：根据 ID 获取指定帖子
@router.get("/posts/{post_id}", response_model=Dict[str, Optional[str]])
async def get_post(post_id: str):
    """
    根据 ID 获取帖子
    """
    post = next((post for post in stored_posts if post["id"] == post_id), None)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

# 路由：添加新帖子
@router.post("/posts", status_code=201)
async def create_post(post: Post):
    """
    创建一个新帖子
    """
    logging.info(f"Received post request with data: {post}")
    new_post = {
        "author": post.author,
        "body": post.body
    }
    stored_posts.insert(0, new_post)
    logging.info(f"Successfully created new post: {new_post}")
    return {"message": "Stored new post.", "post": new_post}









import os
import motor
from typing import Annotated
from pydantic import BeforeValidator
from motor.motor_asyncio import AsyncIOMotorClient


client = AsyncIOMotorClient("mongodb://root:weyon%40mongodb@192.168.15.79:27017,192.168.15.79:27018,192.168.15.79:27019/?replicaSet=app")
db = client.get_database("jobs")
test_collection = db.get_collection("test")

# Represents an ObjectId field in the database.
# It will be represented as a `str` on the model so that it can be serialized to JSON.
PyObjectId = Annotated[str, BeforeValidator(str)]

class MeetingModel(BaseModel):
    """
    Container for a single student record.
    """

    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    title: str = Field(...)
    image: str = Field(...)
    address: str = Field(...)
    description: str = Field(...)


class MeetingCollection(BaseModel):
    """
    A container holding a list of `MeetingModel` instances.

    This exists because providing a top-level array in a JSON response can be a [vulnerability](https://haacked.com/archive/2009/06/25/json-hijacking.aspx/)
    """

    meetings: List[MeetingModel]


@router.post(
    "/meetings/",
    response_description="Add new student",
    response_model=MeetingModel,
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=False,
)
async def create_student(student: MeetingModel = Body(...)):
    """
    Insert a new student record.

    A unique `id` will be created and provided in the response.
    """
    new_student = await test_collection.insert_one(
        student.model_dump(by_alias=True, exclude=["id"])
    )
    created_student = await test_collection.find_one(
        {"_id": new_student.inserted_id}
    )
    return created_student


@router.get(
    "/meetings/",
    response_description="List all students",
    response_model=MeetingCollection,
    response_model_by_alias=False,
)
async def list_students():
    """
    List all of the student data in the database.

    The response is unpaginated and limited to 1000 results.
    """
    return MeetingCollection(meetings=await test_collection.find().to_list(1000))