# -*- coding: utf-8 -*-
# @Time    : 2024/11/1 16:43
# @Author  : Galleons
# @File    : resumes.py

"""
简历数据模型
"""


from typing import Optional, List
from datetime import datetime
from pydantic import ConfigDict, BaseModel, Field, EmailStr
from pydantic.functional_validators import BeforeValidator
from typing_extensions import Annotated
from bson import ObjectId
from uuid import uuid4


class ResumeModel(BaseModel):
    """
    单个学生记录的容器。
    """

    # 学生模型的主键，存储为实例上的 `str`。
    # 这将在发送到 MongoDB 时别名为 `_id`，
    # 但在 API 请求和响应中提供为 `id`。
    name: str = Field(...)
    email: EmailStr = Field(...)
    major: str = Field(...)
    gpa: float = Field(..., le=4.0)
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "name": "柳佳龙",
                "email": "jdoe@example.com",
                "major": "数据科学",
                "gpa": 3.0,
            }
        },
    )

class UpdateResumeModel(BaseModel):
    """
    要对数据库中的文档进行的可选更新集。
    """

    name: Optional[str] = None
    email: Optional[EmailStr] = None
    major: Optional[str] = None
    gpa: Optional[float] = None
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                "name": "柳佳龙",
                "email": "jdoe@example.com",
                "major": "纳米光子学",
                "gpa": 3.0,
            }
        },
    )

class StudentCollection(BaseModel):
    """
    一个容器，包含多个 `StudentModel` 实例。
    这是因为在 JSON 响应中提供最高级数组可能存在漏洞。
    """

    students: List[ResumeModel]
