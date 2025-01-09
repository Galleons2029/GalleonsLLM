import pika
import json
from bson import json_util

def on_message_received(channel, method, properties, body):
    # 解码 JSON 字符串
    message = json.loads(body, object_hook=json_util.object_hook)

    # 打印消息以验证
    print("Received message:", message)

    # 确认消息已正确处理
    channel.basic_ack(delivery_tag=method.delivery_tag)

# 连接到 RabbitMQ 服务器
connection_parameters = pika.ConnectionParameters('localhost')
connection = pika.BlockingConnection(connection_parameters)
channel = connection.channel()

# 确保队列存在
queue_name = 'test_queue'
channel.queue_declare(queue=queue_name, durable=True)

# 开始监听队列
channel.basic_consume(queue=queue_name, on_message_callback=on_message_received)

print("Starting to consume...")
channel.start_consuming()
