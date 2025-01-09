from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

from app.config import settings


class MongoDatabaseConnector:
    """用于连接到 MongoDB 数据库的单例类。"""

    _instance: MongoClient = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            try:
                cls._instance = MongoClient(settings.MONGO_DATABASE_HOST)
            except ConnectionFailure as e:
                print(f"无法连接至数据库: {str(e)}")
                raise

        print(
            f"连接至数据库: {settings.MONGO_DATABASE_HOST} "
        )
        return cls._instance

    def get_database(self):
        return self._instance[settings.MONGO_DATABASE_NAME]

    def close(self):
        if self._instance:
            self._instance.close()
            print("数据库连接已关闭。")


connection = MongoDatabaseConnector()

