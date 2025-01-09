from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

from app.config import settings


def check_or_create_collection(db, collection_name, initial_data=None):
    """
    检查或创建集合。如果集合不存在，则创建它并插入初始数据。
    """
    if collection_name not in db.list_collection_names():
        collection = db[collection_name]
        if initial_data:
            collection.insert_one(initial_data)
        print(f"集合 '{collection_name}' 已创建并添加了初始数据。")
    else:
        print(f"集合 '{collection_name}' 已存在。")


def initialize_db():
    try:
        # 尝试连接到 MongoDB
        client = MongoClient(settings.MONGO_DATABASE_HOST)
        client.admin.command('ping')  # 发送 ping 命令以检查连接是否成功

        # 创建或连接到学校数据库
        school_db = client['school_db']
        # 检查或创建 '长沙理工大学' 集合
        check_or_create_collection(school_db, '长沙理工大学',
                                   {"name": "长沙理工大学", "location": "长沙", "student_count": 12000})

        # 创建或连接到用户数据库
        user_db = client['user_db']
        # 创建用户集合并设置索引
        users = user_db['users']
        users.create_index("用户名", unique=True)
        users.create_index("邮箱", unique=True)
        # 检查或创建用户集合并添加示例用户
        check_or_create_collection(user_db, 'users',
                                   {"username": "john_doe", "email": "john@example.com", "role": "教师"})

        print("数据库初始化完成。")

    except ConnectionFailure:
        print("无法连接到 MongoDB，请检查您的 MongoDB 服务器。")
    except Exception as e:
        print(f"发生错误：{e}")


if __name__ == '__main__':
    initialize_db()
