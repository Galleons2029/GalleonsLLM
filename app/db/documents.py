"""
documents.py模块是与 MongoDB 交互的基础框架。
我们的数据建模以创建特定文档类为中心——UserDocument 、 RepositoryDocument 、 PostDocument和ArticleDocument
这些反映了 MongoDB 集合的结构。
这些类定义了存储的每种数据类型的模式，例如用户详细信息、存储库元数据、帖子内容和文章信息。
通过使用这些类可以确保插入数据库的数据是一致的、有效的，并且易于检索以进行进一步的操作。
"""

import uuid
from typing import List, Optional

from app.errors import ImproperlyConfigured
from pydantic import UUID4, BaseModel, ConfigDict, Field
from pymongo import errors
from app.utils.logging import get_logger

from app.db.mongo import connection

_database = connection.get_database("scrabble")

logger = get_logger(__name__)


class BaseDocument(BaseModel):
    id: UUID4 = Field(default_factory=uuid.uuid4)

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    @classmethod
    def from_mongo(cls, data: dict):
        """将 "_id" (str object) 转换为 "id" (UUID object)."""
        if not data:
            return data

        id = data.pop("_id", None)
        return cls(**dict(data, id=id))

    def to_mongo(self, **kwargs) -> dict:
        """将 "id" (UUID object) 转换为 "_id" (str object)，使得模型实例转换为 MongoDB 友好格式。"""
        exclude_unset = kwargs.pop("exclude_unset", False)
        by_alias = kwargs.pop("by_alias", True)

        parsed = self.model_dump(
            exclude_unset=exclude_unset, by_alias=by_alias, **kwargs
        )

        if "_id" not in parsed and "id" in parsed:
            parsed["_id"] = str(parsed.pop("id"))

        return parsed

    def save(self, **kwargs):
        """使用 PyMongo中insert_one添加文档，并返回 MongoDB 的确认作为插入的 ID。"""
        collection = _database[self._get_collection_name()]

        try:
            result = collection.insert_one(self.to_mongo(**kwargs))
            return result.inserted_id
        except errors.WriteError:
            logger.exception("文档插入失败。")

            return None

    @classmethod
    def get_or_create(cls, **filter_options) -> Optional[str]:
        """获取现有文档或创建新文档，确保无缝数据更新。"""
        collection = _database[cls._get_collection_name()]
        try:
            instance = collection.find_one(filter_options)
            if instance:
                return str(cls.from_mongo(instance).id)
            new_instance = cls(**filter_options)
            new_instance = new_instance.save()
            return new_instance
        except errors.OperationFailure:
            logger.exception("文档创建或者检索失败。")

            return None

    @classmethod
    def bulk_insert(cls, documents: List, **kwargs) -> Optional[List[str]]:
        """用insert_many添加多个文档并返回其 ID。"""
        collection = _database[cls._get_collection_name()]
        try:
            result = collection.insert_many(
                [doc.to_mongo(**kwargs) for doc in documents]
            )
            return result.inserted_ids
        except errors.WriteError:
            logger.exception("文档插入失败。")

            return None

    @classmethod
    def _get_collection_name(cls):
        if not hasattr(cls, "Settings") or not hasattr(cls.Settings, "name"):
            raise ImproperlyConfigured(
                "Document should define an Settings configuration class with the name of the collection."
            )

        return cls.Settings.name


# 使用 Pydantic 模型，每个类确保数据在输入数据库之前正确构造和验证。

class UserDocument(BaseDocument):
    first_name: str
    last_name: str

    class Settings:
        name = "users"


class RepositoryDocument(BaseDocument):
    name: str
    link: str
    content: dict
    owner_id: str = Field(alias="owner_id")

    class Settings:
        name = "repositories"


class PostDocument(BaseDocument):
    platform: str
    content: dict
    author_id: str = Field(alias="author_id")

    class Settings:
        name = "posts"


class ArticleDocument(BaseDocument):
    platform: str
    link: str
    content: dict
    author_id: str = Field(alias="author_id")

    class Settings:
        name = "articles"
