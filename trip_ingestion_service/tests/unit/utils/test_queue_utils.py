import pytest
from unittest.mock import AsyncMock, patch, MagicMock, Mock
from src.utils.queue_utils import QueueUtilFactory, InMemoryQueueUtil, RabbitMQQueueUtil
from src.config import QueueConfig
from src.models.Trip import Trip

@pytest.mark.asyncio
async def test_factory_returns_inmemory_queue_util(monkeypatch):
    config = QueueConfig()
    config.driver = "in_memory"
    factory = QueueUtilFactory(config)
    util = await factory.getQueueUtil()
    assert isinstance(util, InMemoryQueueUtil)
    # Should return the same instance (singleton)
    util2 = await factory.getQueueUtil()
    assert util is util2

@pytest.mark.asyncio
async def test_factory_raises_on_invalid_driver():
    config = QueueConfig()
    config.driver = "invalid_driver"
    factory = QueueUtilFactory(config)
    with pytest.raises(ValueError):
        await factory.getQueueUtil()

@pytest.mark.asyncio
async def test_factory_returns_rabbitmq_queue_util():
    config = QueueConfig()
    config.driver = "rabbitmq"
    factory = QueueUtilFactory(config)

    util = await factory.getQueueUtil()
    assert isinstance(util, RabbitMQQueueUtil)
    # Should return the same instance (singleton)
    util2 = await factory.getQueueUtil()
    assert util is util2

@pytest.mark.asyncio
async def test_rabbitmq_queue_util_create():
    mock_connection = AsyncMock()
    mock_channel = AsyncMock()
    with patch('src.utils.queue_utils.connect_robust', AsyncMock(return_value=mock_connection)) as mock_connect:
        mock_connection.channel.return_value = mock_channel
        mock_channel.declare_queue = AsyncMock()
        util = await RabbitMQQueueUtil.create(
            host='testhost', port=1234, user='guest', password='guest', queue_name='trips_test'
        )
        mock_connect.assert_awaited_once_with('amqp://guest:guest@testhost:1234/')
        mock_connection.channel.assert_awaited_once()
        mock_channel.declare_queue.assert_awaited_once_with('trips_test')
        assert isinstance(util, RabbitMQQueueUtil)
        assert util.connection == mock_connection
        assert util.channel == mock_channel
        assert util.queue_name == 'trips_test'

@pytest.mark.asyncio
async def test_rabbitmq_queue_util_push():
    mock_channel = Mock()
    mock_exchange = AsyncMock()
    mock_channel.default_exchange = mock_exchange
    util = RabbitMQQueueUtil(connection=None, channel=mock_channel, queue_name='trips_test')
    trip = Trip(
        trip_id='id', location='loc', country='IE',
        start=None, stops=[], end=None
    )
    await util.push(trip)
    assert mock_exchange.publish.await_count == 1
    args, kwargs = mock_exchange.publish.await_args
    assert kwargs['routing_key'] == 'trips_test'
