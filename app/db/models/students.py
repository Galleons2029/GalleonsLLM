# -*- coding: utf-8 -*-
# @Time    : 2024/11/1 16:04
# @Author  : Galleons
# @File    : students.py

"""
学生数据模型
"""


from typing import Optional, List
from datetime import datetime
from pydantic import ConfigDict, BaseModel, Field, EmailStr
from pydantic.functional_validators import BeforeValidator
from typing_extensions import Annotated
from bson import ObjectId
from uuid import uuid4
from app.db.models.user import UserBase
from app.db.models.resumes import ResumeModel

# 表示数据库中的 ObjectId 字段。
# 它将在模型中表示为 `str`，以便可以序列化为 JSON。
PyObjectId = Annotated[str, BeforeValidator(str)]

class StudentModel(UserBase):
    """
    单个学生记录的容器。
    """

    # 学生模型的主键，存储为实例上的 `str`。
    # 这将在发送到 MongoDB 时别名为 `_id`，
    # 但在 API 请求和响应中提供为 `id`。
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
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



class UpdateStudentModel(BaseModel):
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

    students: List[StudentModel]



class DocumentCollection(BaseModel):
    """
    一个容器，包含多个 `StudentModel` 实例。
    这是因为在 JSON 响应中提供最高级数组可能存在漏洞。
    """

    students: List[StudentModel]
