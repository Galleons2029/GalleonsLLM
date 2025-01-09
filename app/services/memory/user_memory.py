# -*- coding: utf-8 -*-
# @Time    : 2024/10/30 14:54
# @Author  : Galleons
# @File    : user_memory.py

"""
这里是文件说明
"""

from mem0 import Memory
from mem0.proxy.main import Mem0

config = {
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "host": "localhost",
            "port": 6333,
        }
    },
    "llm": {
            "provider": "openai",
            "config": {
                # Provider-specific settings go here
                "api_key": "sk-gxijztovbtakciuwjwwqyaoxarjfvhuargxkoawhuzsanssm",
                "openai_base_url": "https://api.siliconflow.cn/v1",
            }
        }
}

m = Memory.from_config(config)

# For a user
result = m.add("我非常喜欢使用学习统计学", user_id="alice", metadata={"category": "hobbies"})

related_memories = m.search(query="帮我规划一下周末", user_id="alice")
# messages = [
#    {"role": "user", "content": "Hi, I'm Alex. I like to play cricket on weekends."},
#    {"role": "assistant", "content": "Hello Alex! It's great to know that you enjoy playing cricket on weekends. I'll remember that for future reference."}
# ]
# client.add(messages, user_id="alice")


# # Get all memories
# all_memories = m.get_all(user_id="alice")
#
# client = Mem0(api_key="m0-xxx")
