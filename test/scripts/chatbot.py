# -*- coding: utf-8 -*-
# @Time    : 2025/1/2 17:55
# @Author  : Galleons
# @File    : chatbot.py

"""
这里是文件说明
"""

from openai import OpenAI
import streamlit as st

st.title("💬 RAG测试页")
st.caption("🚀 基于知识库支持查询")
# with st.sidebar:
#     openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
#     "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"
#     "[View the source code](https://github.com/streamlit/llm-examples/blob/main/Chatbot.py)"
#     "[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/streamlit/llm-examples?quickstart=1)"
openai_api_key = 'sk-gxijztovbtakciuwjwwqyaoxarjfvhuargxkoawhuzsanssm'
client = OpenAI(base_url="https://api.siliconflow.cn/v1", api_key=openai_api_key)

# 默认模型
# Set a default model
if "openai_model" not in st.session_state:
    st.session_state["model"] = "Qwen/Qwen2.5-72B-Instruct"

# 初始化对话历史
if "messages" not in st.session_state:
    st.session_state.messages = []

# 在应用重新运行时显示历史聊天消息
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "你好！"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    if not openai_api_key:
        st.info("请输入需要加载的知识库")
        st.stop()

    # client = OpenAI(api_key=openai_api_key)

    # 1. 添加用户消息到对话历史
    st.session_state.messages.append({"role": "user", "content": prompt})
    # st.chat_message("user").write(prompt)
    with st.chat_message("user"):
        st.markdown(prompt)


    # 2. 调用 API 发送请求
    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model=st.session_state["model"],
            messages=[
                {"role": message["role"], "content": message["content"]}
                for message in st.session_state.messages
            ],
            stream=True,
        )
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})

    # response = client.chat.completions.create(
    #     # model="Qwen/Qwen2.5-7B-Instruct",
    #     messages=st.session_state.messages,
    #     stream=True,
    # )

    # # 3. 获取并添加助手回复
    # msg = response.choices[0].message.content
    # st.session_state.messages.append({"role": "assistant", "content": msg})
    # st.chat_message("assistant").write(msg)