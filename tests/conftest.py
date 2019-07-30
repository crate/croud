import aiohttp
import pytest

from tests.util.fake_server import FakeCrateDBCloud, FakeResolver


@pytest.fixture
async def fake_cloud_connector(event_loop):
    async with FakeCrateDBCloud(loop=event_loop) as dns_info:
        resolver = FakeResolver(dns_info, loop=event_loop)
        yield aiohttp.TCPConnector(loop=event_loop, resolver=resolver, ssl=True)
