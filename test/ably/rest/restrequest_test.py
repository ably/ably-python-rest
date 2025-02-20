import httpx
import pytest
import respx

from ably import AblyRest
from ably.http.paginatedresult import HttpPaginatedResponse
from ably.transport.defaults import Defaults
from test.ably.testapp import TestApp
from test.ably.utils import BaseAsyncTestCase
from test.ably.utils import VaryByProtocolTestsMetaclass, dont_vary_protocol


# RSC19
class TestRestRequest(BaseAsyncTestCase, metaclass=VaryByProtocolTestsMetaclass):

    async def asyncSetUp(self):
        self.ably = await TestApp.get_ably_rest()
        self.test_vars = await TestApp.get_test_vars()

        # Populate the channel (using the new api)
        self.channel = self.get_channel_name()
        self.path = '/channels/%s/messages' % self.channel
        for i in range(20):
            body = {'name': 'event%s' % i, 'data': 'lorem ipsum %s' % i}
            await self.ably.request('POST', self.path, body=body, version=Defaults.protocol_version)

    async def asyncTearDown(self):
        await self.ably.close()

    def per_protocol_setup(self, use_binary_protocol):
        self.ably.options.use_binary_protocol = use_binary_protocol
        self.use_binary_protocol = use_binary_protocol

    async def test_post(self):
        body = {'name': 'test-post', 'data': 'lorem ipsum'}
        result = await self.ably.request('POST', self.path, body=body, version=Defaults.protocol_version)

        assert isinstance(result, HttpPaginatedResponse)  # RSC19d
        # HP3
        assert type(result.items) is list
        assert len(result.items) == 1
        assert result.items[0]['channel'] == self.channel
        assert 'messageId' in result.items[0]

    async def test_get(self):
        params = {'limit': 10, 'direction': 'forwards'}
        result = await self.ably.request('GET', self.path, params=params, version=Defaults.protocol_version)

        assert isinstance(result, HttpPaginatedResponse)  # RSC19d

        # HP2
        assert isinstance(await result.next(), HttpPaginatedResponse)
        assert isinstance(await result.first(), HttpPaginatedResponse)

        # HP3
        assert isinstance(result.items, list)
        item = result.items[0]
        assert isinstance(item, dict)
        assert 'timestamp' in item
        assert 'id' in item
        assert item['name'] == 'event0'
        assert item['data'] == 'lorem ipsum 0'

        assert result.status_code == 200     # HP4
        assert result.success is True        # HP5
        assert result.error_code is None     # HP6
        assert result.error_message is None  # HP7
        assert isinstance(result.headers, list)   # HP7

    @dont_vary_protocol
    async def test_not_found(self):
        result = await self.ably.request('GET', '/not-found', version=Defaults.protocol_version)
        assert isinstance(result, HttpPaginatedResponse)  # RSC19d
        assert result.status_code == 404             # HP4
        assert result.success is False               # HP5

    @dont_vary_protocol
    async def test_error(self):
        params = {'limit': 'abc'}
        result = await self.ably.request('GET', self.path, params=params, version=Defaults.protocol_version)
        assert isinstance(result, HttpPaginatedResponse)  # RSC19d
        assert result.status_code == 400  # HP4
        assert not result.success
        assert result.error_code
        assert result.error_message

    async def test_headers(self):
        key = 'X-Test'
        value = 'lorem ipsum'
        result = await self.ably.request('GET', '/time', headers={key: value}, version=Defaults.protocol_version)
        assert result.response.request.headers[key] == value

    # RSC19e
    @dont_vary_protocol
    async def test_timeout(self):
        # Timeout
        timeout = 0.000001
        ably = AblyRest(token="foo", http_request_timeout=timeout)
        assert ably.http.http_request_timeout == timeout
        with pytest.raises(httpx.ReadTimeout):
            await ably.request('GET', '/time', version=Defaults.protocol_version)
        await ably.close()

        default_endpoint = 'https://sandbox.realtime.ably-nonprod.net/time'
        fallback_host = 'sandbox.a.fallback.ably-realtime-nonprod.com'
        fallback_endpoint = f'https://{fallback_host}/time'
        ably = await TestApp.get_ably_rest(fallback_hosts=[fallback_host])
        with respx.mock:
            default_route = respx.get(default_endpoint)
            fallback_route = respx.get(fallback_endpoint)
            headers = {
                "Content-Type": "application/json"
            }
            default_route.side_effect = httpx.ConnectError('')
            fallback_route.return_value = httpx.Response(200, headers=headers, text='[123]')
            await ably.request('GET', '/time', version=Defaults.protocol_version)
        await ably.close()

        # Bad host, no Fallback
        ably = AblyRest(key=self.test_vars["keys"][0]["key_str"],
                        rest_host='some.other.host',
                        port=self.test_vars["port"],
                        tls_port=self.test_vars["tls_port"],
                        tls=self.test_vars["tls"])
        with pytest.raises(httpx.ConnectError):
            await ably.request('GET', '/time', version=Defaults.protocol_version)
        await ably.close()

    async def test_version(self):
        version = "150"  # chosen arbitrarily
        result = await self.ably.request('GET', '/time', "150")
        assert result.response.request.headers["X-Ably-Version"] == version
