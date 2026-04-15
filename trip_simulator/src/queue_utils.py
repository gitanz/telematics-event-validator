import json
from abc import ABC, abstractmethod
from typing import Union, Any

from aio_pika import connect_robust, Message
from aio_pika.abc import AbstractIncomingMessage
from aio_pika.exceptions import QueueEmpty

from config import QueueConfig
from trip import Trip


class QueueUtilInterface(ABC):
    @abstractmethod
    async def push(self, trip: Trip) -> None:
        """Push a Trip object to the queue."""
        pass

    @abstractmethod
    async def pop(self) -> Union[Any, None]:
        """Pop a Trip object from the queue."""
        pass



class InMemoryQueueUtil(QueueUtilInterface):
    def __init__(self):
        self.queue = []

    async def push(self, trip: Trip) -> None:
        self.queue.append(trip)

    async def pop(self) -> Union[Trip, None]:
        if not self.queue:
            return None
        return self.queue.pop(0)



class RabbitMQQueueUtil(QueueUtilInterface):
    def __init__(self, connection, channel, queue_name):
        self.connection = connection
        self.channel = channel
        self.queue_name = queue_name

    @classmethod
    async def create(cls, host: str, port: int, user: str, password: str, queue_name: str = "trips"):
        connection = await connect_robust(f"amqp://{user}:{password}@{host}:{port}/")
        channel = await connection.channel()
        await channel.declare_queue(queue_name)
        return cls(connection, channel, queue_name)

    async def push(self, trip: Trip) -> None:
        print(trip.to_dict())
        message = Message(body=json.dumps(trip.to_dict()).encode())
        await self.channel.default_exchange.publish(message, routing_key=self.queue_name)

    async def pop(self) -> Union[AbstractIncomingMessage, None]:
        queue = await self.channel.declare_queue(self.queue_name, passive=True)

        try:
            message = await queue.get(timeout=1)
            if message is None:
                return None
            return message
        except QueueEmpty as e:
            return None


class QueueUtilFactory:
    inmemory_queue_util: InMemoryQueueUtil = None
    rabbit_queue_util: RabbitMQQueueUtil = None

    def __init__(self, queue_config: QueueConfig):
        self.queue_config = queue_config

    async def getQueueUtil(self) -> QueueUtilInterface:
        if self.queue_config.driver == "in_memory":
            if self.inmemory_queue_util is None:
                self.inmemory_queue_util = InMemoryQueueUtil()
            return self.inmemory_queue_util

        if self.queue_config.driver == "rabbitmq":
            if self.rabbit_queue_util is None:
                self.rabbit_queue_util = await RabbitMQQueueUtil.create(
                    host=self.queue_config.host,
                    port=self.queue_config.port,
                    user=self.queue_config.user,
                    password=self.queue_config.password,
                    queue_name=getattr(self.queue_config, 'queue_name', 'trips')
                )
            return self.rabbit_queue_util

        raise ValueError(f"Unsupported queue driver: {self.queue_config.driver}")
