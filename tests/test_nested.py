import json

import pytest

from .tunnel import Tunnel


@pytest.fixture
def tunnel_json():
    return """
        {
            "name": "my_tunnel",
            "outgoing_bytes": 5,
            "proxyid": [
                {
                    "p2name": "my_proxy",
                    "status": "UP",
                    "incoming_bytes": 3,
                    "outgoing_bytes": 2
                }
            ]
        }
        """


def test_nested_model(tunnel_json):
    parsed_tunnel_data = json.loads(tunnel_json)

    tunnel = Tunnel.model_validate(parsed_tunnel_data)
    sorted_mint_lines = sorted(tunnel.to_mint_lines())

    assert sorted_mint_lines == [
        'fortigate.tunnel.bytes.out.count,tunnel="my_tunnel" count,5',
        'fortigate.tunnel.proxy.bytes.in.count,tunnel="my_tunnel",proxy="my_proxy",status="UP" count,3',
        'fortigate.tunnel.proxy.bytes.out.count,tunnel="my_tunnel",proxy="my_proxy",status="UP" count,2',
        'fortigate.tunnel.proxy.status,tunnel="my_tunnel",proxy="my_proxy",status="UP" gauge,1',
    ]
