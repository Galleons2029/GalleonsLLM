import pika

from app.config import settings


class RabbitMQConnection:
    """用于管理 RabbitMQ 连接的单例类。"""

    _instance = None

    def __new__(
        cls,
        host: str = None,
        port: int = None,
        username: str = None,
        password: str = None,
        virtual_host: str = "/",
    ):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
        self,
        host: str = None,
        port: int = None,
        username: str = None,
        password: str = None,
        virtual_host: str = "/",
        fail_silently: bool = False,
        **kwargs,
    ):
        self.host = host or settings.RABBITMQ_HOST
        self.port = port or settings.RABBITMQ_PORT
        self.username = username or settings.RABBITMQ_DEFAULT_USERNAME
        self.password = password or settings.RABBITMQ_DEFAULT_PASSWORD
        self.virtual_host = virtual_host
        self.fail_silently = fail_silently
        self._connection = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def connect(self):
        try:
            credentials = pika.PlainCredentials(self.username, self.password)
            self._connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=self.host,
                    port=self.port,
                    virtual_host=self.virtual_host,
                    credentials=credentials,
                )
            )
        except pika.exceptions.AMQPConnectionError as e:
            print("RabbitMQ 连接失败:", e)
            if not self.fail_silently:
                raise e

    def is_connected(self) -> bool:
        return self._connection is not None and self._connection.is_open

    def get_channel(self):
        if self.is_connected():
            return self._connection.channel()

    def close(self):
        if self.is_connected():
            self._connection.close()
            self._connection = None
            print("关闭 RabbitMQ 连接")


def publish_to_rabbitmq(queue_name: str, data: str):
    """将数据推送到 RabbitMQ 队列。 """
    try:
        # 创建 RabbitMQConnection 的实例
        rabbitmq_conn = RabbitMQConnection()

        # 使用 with 自动管理连接的开启和关闭
        with rabbitmq_conn:
            channel = rabbitmq_conn.get_channel()

            # 确保队列存在，如果不存在则创建，设置为持久化
            channel.queue_declare(queue=queue_name, durable=True)

            # 开启发送确认，确保消息被服务器接受
            channel.confirm_delivery()

            # 发送数据到指定队列
            channel.basic_publish(
                exchange="",
                routing_key=queue_name,
                body=data,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # 将消息设置为持久化
                ),
            )
            print("发送数据到 RabbitMQ:", data)
    except pika.exceptions.UnroutableError:
        print("消息无法被路由")
    except Exception as e:
        print(f"RabbitMQ 连接错误: {e}")


if __name__ == "__main__":
    publish_to_rabbitmq("test_queue", "Hello, World!")
