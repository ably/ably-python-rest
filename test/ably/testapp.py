import json
import os
import logging

from ably.rest.rest import AblyRest
from ably.types.capability import Capability
from ably.types.options import Options
from ably.util.exceptions import AblyException
from ably.realtime.realtime import AblyRealtime

log = logging.getLogger(__name__)

with open(os.path.dirname(__file__) + '/../assets/testAppSpec.json', 'r') as f:
    app_spec_local = json.loads(f.read())

tls = (os.environ.get('ABLY_TLS') or "true").lower() == "true"
rest_host = os.environ.get('ABLY_REST_HOST', 'sandbox.realtime.ably-nonprod.net')
realtime_host = os.environ.get('ABLY_REALTIME_HOST', 'sandbox.realtime.ably-nonprod.net')

environment = os.environ.get('ABLY_ENV', 'nonprod:sandbox')

port = 80
tls_port = 443

if rest_host and not rest_host.endswith("realtime.ably-nonprod.net"):
    tls = tls and rest_host != "localhost"
    port = 8080
    tls_port = 8081


ably = AblyRest(token='not_a_real_token',
                port=port, tls_port=tls_port, tls=tls,
                environment=environment,
                use_binary_protocol=False)


class TestApp:
    __test_vars = None

    @staticmethod
    async def get_test_vars():
        if not TestApp.__test_vars:
            r = await ably.http.post("/apps", body=app_spec_local, skip_auth=True)
            AblyException.raise_for_response(r)

            app_spec = r.json()

            app_id = app_spec.get("appId", "")

            test_vars = {
                "app_id": app_id,
                "host": rest_host,
                "port": port,
                "tls_port": tls_port,
                "tls": tls,
                "environment": environment,
                "realtime_host": realtime_host,
                "keys": [{
                    "key_name": "%s.%s" % (app_id, k.get("id", "")),
                    "key_secret": k.get("value", ""),
                    "key_str": "%s.%s:%s" % (app_id, k.get("id", ""), k.get("value", "")),
                    "capability": Capability(json.loads(k.get("capability", "{}"))),
                } for k in app_spec.get("keys", [])]
            }

            TestApp.__test_vars = test_vars
            log.debug([(app_id, k.get("id", ""), k.get("value", ""))
                      for k in app_spec.get("keys", [])])

        return TestApp.__test_vars

    @staticmethod
    async def get_ably_rest(**kw):
        test_vars = await TestApp.get_test_vars()
        options = TestApp.get_options(test_vars, **kw)
        options.update(kw)
        return AblyRest(**options)

    @staticmethod
    async def get_ably_realtime(**kw):
        test_vars = await TestApp.get_test_vars()
        options = TestApp.get_options(test_vars, **kw)
        return AblyRealtime(**options)

    @staticmethod
    def get_options(test_vars, **kwargs):
        options = {
            'port': test_vars["port"],
            'tls_port': test_vars["tls_port"],
            'tls': test_vars["tls"],
            'environment': test_vars["environment"],
        }
        auth_methods = ["auth_url", "auth_callback", "token", "token_details", "key"]
        if not any(x in kwargs for x in auth_methods):
            options["key"] = test_vars["keys"][0]["key_str"]

        if any(x in kwargs for x in ["rest_host", "realtime_host"]):
            options["environment"] = None

        options.update(kwargs)

        return options

    @staticmethod
    async def clear_test_vars():
        test_vars = TestApp.__test_vars
        options = Options(key=test_vars["keys"][0]["key_str"])
        options.rest_host = test_vars["host"]
        options.port = test_vars["port"]
        options.tls_port = test_vars["tls_port"]
        options.tls = test_vars["tls"]
        ably = await TestApp.get_ably_rest()
        await ably.http.delete('/apps/' + test_vars['app_id'])
        TestApp.__test_vars = None
        await ably.close()
