import json
from datetime import datetime

import pytest
from dynatrace_extension import Metric, MetricType, DtEventType

from dynatrace_extension_models import Event

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
    tunnel = Tunnel(**parsed_tunnel_data)

    # Evaluate explicitly with a preset datetime
    now = datetime.now()
    tunnel.evaluate(timestamp=now)

    # Here is what model gives us
    sorted_mint_lines = sorted(tunnel.mint_lines)
    sorted_event_dicts = sorted([str(x) for x in tunnel.event_dicts])
    
    print("That's what was generated")
    for sml in sorted_mint_lines:
        print(sml)
    for sed in sorted_event_dicts:
        print(sed)

    # Here is the same set of metrics and events created manually
    metrics = [
        Metric("fortigate.tunnel.bytes.out.count", 5, {"tunnel": "my_tunnel"}, MetricType.COUNT, timestamp=now),
        Metric("fortigate.tunnel.proxy.bytes.in.count", 3, {"proxy": "my_proxy", "status": "UP", "tunnel": "my_tunnel"}, metric_type=MetricType.COUNT, timestamp=now),
        Metric("fortigate.tunnel.proxy.bytes.out.count", 2, {"proxy": "my_proxy", "status": "UP", "tunnel": "my_tunnel"}, metric_type=MetricType.COUNT, timestamp=now),
        Metric("fortigate.tunnel.proxy.status", 1, {"proxy": "my_proxy", "status": "UP", "tunnel": "my_tunnel"}, timestamp=now),
    ]
    sorted_metrics = sorted([m.to_mint_line() for m in metrics])
    events = [
        Event(title="Small outgoing traffic!", event_type=DtEventType.CUSTOM_INFO),
        Event(title="Proxy my_proxy is slow!", event_type=DtEventType.CUSTOM_ALERT, properties={"proxy": "my_proxy", "status": "UP", "tunnel": "my_tunnel"}),
    ]
    sorted_events = sorted([str(x.to_dict()) for x in events])
    
    print("That's what we should have")
    for sm in sorted_metrics:
        print(sm)
    for se in sorted_events:
        print(se)


    assert sorted_mint_lines == sorted_metrics and sorted_event_dicts == sorted_events
