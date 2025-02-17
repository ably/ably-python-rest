import random
import logging

from ably.transport.defaults import Defaults
from ably.types.authoptions import AuthOptions

log = logging.getLogger(__name__)


class Options(AuthOptions):
    def __init__(self, client_id=None, log_level=0, tls=True, rest_host=None, realtime_host=None, port=0,
                 tls_port=0, use_binary_protocol=True, queue_messages=False, recover=False, endpoint=None,
                 environment=None, http_open_timeout=None, http_request_timeout=None,
                 realtime_request_timeout=None, http_max_retry_count=None, http_max_retry_duration=None,
                 fallback_hosts=None, fallback_retry_timeout=None, disconnected_retry_timeout=None,
                 idempotent_rest_publishing=None, loop=None, auto_connect=True,
                 suspended_retry_timeout=None, connectivity_check_url=None,
                 channel_retry_timeout=Defaults.channel_retry_timeout, add_request_ids=False, **kwargs):

        super().__init__(**kwargs)

        # TODO check these defaults
        if fallback_retry_timeout is None:
            fallback_retry_timeout = Defaults.fallback_retry_timeout

        if realtime_request_timeout is None:
            realtime_request_timeout = Defaults.realtime_request_timeout

        if disconnected_retry_timeout is None:
            disconnected_retry_timeout = Defaults.disconnected_retry_timeout

        if connectivity_check_url is None:
            connectivity_check_url = Defaults.connectivity_check_url

        connection_state_ttl = Defaults.connection_state_ttl

        if suspended_retry_timeout is None:
            suspended_retry_timeout = Defaults.suspended_retry_timeout

        if environment is not None and rest_host is not None:
            raise ValueError('specify rest_host or environment, not both')

        if environment is not None and realtime_host is not None:
            raise ValueError('specify realtime_host or environment, not both')

        if environment is not None and endpoint is not None:
            raise ValueError('specify endpoint or environment, not both')

        if idempotent_rest_publishing is None:
            from ably import api_version
            idempotent_rest_publishing = api_version >= '1.2'

        if environment == "production":
            endpoint = Defaults.endpoint

        if environment is not None and endpoint is None:
            endpoint = environment

        if endpoint is None:
            endpoint = Defaults.endpoint

        self.__client_id = client_id
        self.__log_level = log_level
        self.__tls = tls
        self.__rest_host = rest_host
        self.__realtime_host = realtime_host
        self.__port = port
        self.__tls_port = tls_port
        self.__use_binary_protocol = use_binary_protocol
        self.__queue_messages = queue_messages
        self.__recover = recover
        self.__endpoint = endpoint
        self.__http_open_timeout = http_open_timeout
        self.__http_request_timeout = http_request_timeout
        self.__realtime_request_timeout = realtime_request_timeout
        self.__http_max_retry_count = http_max_retry_count
        self.__http_max_retry_duration = http_max_retry_duration
        self.__fallback_hosts = fallback_hosts
        self.__fallback_retry_timeout = fallback_retry_timeout
        self.__disconnected_retry_timeout = disconnected_retry_timeout
        self.__channel_retry_timeout = channel_retry_timeout
        self.__idempotent_rest_publishing = idempotent_rest_publishing
        self.__loop = loop
        self.__auto_connect = auto_connect
        self.__connection_state_ttl = connection_state_ttl
        self.__suspended_retry_timeout = suspended_retry_timeout
        self.__connectivity_check_url = connectivity_check_url
        self.__fallback_realtime_host = None
        self.__add_request_ids = add_request_ids

        self.__rest_hosts = self.__get_rest_hosts()
        self.__realtime_hosts = self.__get_realtime_hosts()

    @property
    def client_id(self):
        return self.__client_id

    @client_id.setter
    def client_id(self, value):
        self.__client_id = value

    @property
    def log_level(self):
        return self.__log_level

    @log_level.setter
    def log_level(self, value):
        self.__log_level = value

    @property
    def tls(self):
        return self.__tls

    @tls.setter
    def tls(self, value):
        self.__tls = value

    @property
    def rest_host(self):
        return self.__rest_host

    @rest_host.setter
    def rest_host(self, value):
        self.__rest_host = value

    # RTC1d
    @property
    def realtime_host(self):
        return self.__realtime_host

    @realtime_host.setter
    def realtime_host(self, value):
        self.__realtime_host = value

    @property
    def port(self):
        return self.__port

    @port.setter
    def port(self, value):
        self.__port = value

    @property
    def tls_port(self):
        return self.__tls_port

    @tls_port.setter
    def tls_port(self, value):
        self.__tls_port = value

    @property
    def use_binary_protocol(self):
        return self.__use_binary_protocol

    @use_binary_protocol.setter
    def use_binary_protocol(self, value):
        self.__use_binary_protocol = value

    @property
    def queue_messages(self):
        return self.__queue_messages

    @queue_messages.setter
    def queue_messages(self, value):
        self.__queue_messages = value

    @property
    def recover(self):
        return self.__recover

    @recover.setter
    def recover(self, value):
        self.__recover = value

    @property
    def endpoint(self):
        return self.__endpoint

    @property
    def http_open_timeout(self):
        return self.__http_open_timeout

    @http_open_timeout.setter
    def http_open_timeout(self, value):
        self.__http_open_timeout = value

    @property
    def http_request_timeout(self):
        return self.__http_request_timeout

    @property
    def realtime_request_timeout(self):
        return self.__realtime_request_timeout

    @http_request_timeout.setter
    def http_request_timeout(self, value):
        self.__http_request_timeout = value

    @property
    def http_max_retry_count(self):
        return self.__http_max_retry_count

    @http_max_retry_count.setter
    def http_max_retry_count(self, value):
        self.__http_max_retry_count = value

    @property
    def http_max_retry_duration(self):
        return self.__http_max_retry_duration

    @http_max_retry_duration.setter
    def http_max_retry_duration(self, value):
        self.__http_max_retry_duration = value

    @property
    def fallback_hosts(self):
        return self.__fallback_hosts

    @property
    def fallback_retry_timeout(self):
        return self.__fallback_retry_timeout

    @property
    def disconnected_retry_timeout(self):
        return self.__disconnected_retry_timeout

    @property
    def channel_retry_timeout(self):
        return self.__channel_retry_timeout

    @property
    def idempotent_rest_publishing(self):
        return self.__idempotent_rest_publishing

    @property
    def loop(self):
        return self.__loop

    # RTC1b
    @property
    def auto_connect(self):
        return self.__auto_connect

    @property
    def connection_state_ttl(self):
        return self.__connection_state_ttl

    @connection_state_ttl.setter
    def connection_state_ttl(self, value):
        self.__connection_state_ttl = value

    @property
    def suspended_retry_timeout(self):
        return self.__suspended_retry_timeout

    @property
    def connectivity_check_url(self):
        return self.__connectivity_check_url

    @property
    def fallback_realtime_host(self):
        return self.__fallback_realtime_host

    @fallback_realtime_host.setter
    def fallback_realtime_host(self, value):
        self.__fallback_realtime_host = value

    @property
    def add_request_ids(self):
        return self.__add_request_ids

    def __get_rest_hosts(self):
        """
        Return the list of hosts as they should be tried. First comes the main
        host. Then the fallback hosts in random order.
        The returned list will have a length of up to http_max_retry_count.
        """
        # Defaults
        host = self.rest_host
        if host is None:
            host = Defaults.get_hostname(self.endpoint)

        http_max_retry_count = self.http_max_retry_count
        if http_max_retry_count is None:
            http_max_retry_count = Defaults.http_max_retry_count

        # Fallback hosts
        fallback_hosts = self.fallback_hosts
        if fallback_hosts is None:
            if self.rest_host:
                fallback_hosts = []
            else:
                fallback_hosts = Defaults.get_fallback_hosts(self.endpoint)

        # Shuffle
        fallback_hosts = list(fallback_hosts)
        random.shuffle(fallback_hosts)
        self.__fallback_hosts = fallback_hosts

        # First main host
        hosts = [host] + fallback_hosts
        hosts = hosts[:http_max_retry_count]
        return hosts

    def __get_realtime_hosts(self):
        if self.realtime_host is not None:
            host = self.realtime_host
            return [host]

        host = Defaults.get_hostname(self.endpoint)
        return [host] + self.__fallback_hosts

    def get_rest_hosts(self):
        return self.__rest_hosts

    def get_rest_host(self):
        return self.__rest_hosts[0]

    def get_realtime_hosts(self):
        return self.__realtime_hosts

    def get_realtime_host(self):
        return self.__realtime_hosts[0]

    def get_fallback_rest_hosts(self):
        return self.__rest_hosts[1:]

    def get_fallback_realtime_hosts(self):
        return self.__realtime_hosts[1:]
