# from openai import OpenAI
#
# client = OpenAI(api_key="sk-orbrjhjcqmgezlurbvsmfxqmnjwkmjdrypwdiwvyfarkbnag", base_url="https://api.siliconflow.cn/v1")
#
# response = client.chat.completions.create(
#     model='alibaba/Qwen2-7B-Instruct',
#     messages=[
#         {'role': 'user', 'content': "抛砖引玉是什么意思呀"}
#     ],
#     stream=True
# )
#
# for chunk in response:
#     print(chunk.choices[0].delta.content)
#
#

import base64

def image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            # 读取二进制数据并转换为base64
            encoded_string = base64.b64encode(image_file.read())
            return encoded_string.decode('utf-8')
    except Exception as e:
        print(f"转换失败: {e}")
        return None

# 使用示例
image_path = "/home/weyon2/DATA/企业微信截图_17274087412178.png"
base64_string = image_to_base64(image_path)
print(base64_string)


import requests

url = "https://api.siliconflow.cn/v1/chat/completions"

# payload = {
#     "model": "deepseek-ai/DeepSeek-V2.5",
#     "messages": [
#         {
#             "role": "user",
#             "content": "SiliconCloud推出分层速率方案与免费模型RPM提升10倍，对于整个大模型应用领域带来哪些改变？"
#         }
#     ],
#     "stream": False,
#     "max_tokens": 512,
#     "stop": "",
#     "temperature": 0.7,
#     "top_p": 0.7,
#     "top_k": 50,
#     "frequency_penalty": 0.5,
#     "n": 1,
#     "response_format": {"type": "text"},
#     "tools": [
#         {
#             "type": "function",
#             "function": {
#                 "description": "<string>",
#                 "name": "<string>",
#                 "parameters": {},
#                 "strict": True
#             }
#         }
#     ]
# }
#
# headers = {
#     "Authorization": "Bearer sk-kutnkphezarrglswegiqwwaywqqwkvanwjobmwmdjututqkf",
#     "Content-Type": "application/json"
# }
#
# response = requests.request("POST", url, json=payload, headers=headers)
#
# print(response.text)
import base64
import imghdr
from pathlib import Path


def image_to_base64(image_path):
    """
    将图片文件转换为base64编码，并识别图片类型

    参数:
        image_path: 图片文件路径（字符串或Path对象）
    返回:
        tuple: (base64编码字符串, 图片类型)
    """
    # 将输入路径转换为Path对象，方便处理
    image_path = Path(image_path)

    # 检查文件是否存在
    if not image_path.exists():
        raise FileNotFoundError(f"找不到图片文件: {image_path}")

    # 以二进制模式读取图片文件
    with open(image_path, 'rb') as img_file:
        # 读取文件内容
        img_data = img_file.read()

        # 使用imghdr识别图片类型
        image_type = imghdr.what(None, img_data)

        if image_type is None:
            raise ValueError(f"无法识别图片类型: {image_path}")

        # 将二进制数据转换为base64编码
        base64_str = base64.b64encode(img_data).decode('utf-8')

        return base64_str, image_type


# 使用示例
try:
    # 调用函数转换图片
    b64_str, img_type = image_to_base64('/home/weyon2/DATA/企业微信截图_17274087412178.png')
    print(f"图片类型: {img_type}")
    print(f"Base64编码 (前50个字符): {b64_str[:50]}...")
except Exception as e:
    print(f"发生错误: {e}")

import json
from openai import OpenAI

client = OpenAI(
    api_key="sk-kutnkphezarrglswegiqwwaywqqwkvanwjobmwmdjututqkf", # 从https://cloud.siliconflow.cn/account/ak获取
    base_url="https://api.siliconflow.cn/v1"
)

response = client.chat.completions.create(
        model="Qwen/Qwen2-VL-72B-Instruct",
        messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/{img_type};base64,{b64_str}"}
                },
                {
                    "type": "text",
                    "text": "描述一下这张图"
                }
            ]
        }],
    stream=True
)

for chunk in response:
    chunk_message = chunk.choices[0].delta.content
    print(chunk_message, end='', flush=True)
