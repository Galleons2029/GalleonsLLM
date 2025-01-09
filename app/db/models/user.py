# -*- coding: utf-8 -*-
# @Time    : 2024/10/29 17:20
# @Author  : Galleons
# @File    : user.py

"""
用户数据模型
"""

from pydantic import BaseModel

class UserBase(BaseModel):
    username: str
    password: str
    email: str

class UserInDB(UserBase):
    id: int
    hashed_password: str
