# dt-extensions-models

<p>
  <a href="https://pypi.org/pypi/dt-extensions-models"><img alt="Package version" src="https://img.shields.io/pypi/v/dt-extensions-models?logo=python&logoColor=white&color=blue"></a>
  <a href="https://pypi.org/pypi/dt-extensions-models"><img alt="Supported python versions" src="https://img.shields.io/pypi/pyversions/dt-extensions-models?logo=python&logoColor=white"></a>
</p>

Helper library implementing best practices for strongly typed models and reporting metrics.

## Installation

```shell
pip install dt-extensions-models
```

## Usage

Use just like you would use Pydantic models in general. However, there are a couple of new additions.

## Example

### Raw data

Imagine a response from an JSON REST API coming in like this:

```json
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
```

### Parsing requirements

and we want to parse it and report 5 metrics and 2 events:

Metrics:

* Counter `fortigate.tunnel.bytes.in.count` for incoming traffic to the tunnel, if any.
* Counter `fortigate.tunnel.bytes.out.count` for outgoing traffic from the tunnel, if any.
* Counter `fortigate.tunnel.proxy.bytes.in.count` for incoming traffic for each of the proxies within the tunnel.
* Counter `fortigate.tunnel.proxy.bytes.out.count` for outgoing traffic for each of the proxies within the tunnel.
* Gauge `fortigate.tunnel.proxy.status` to reflect the overall status of each proxy.

Additionally, we want each proxy metric to have 3 dimensions:

* `status` - status of this proxy. "UP" if it's "up" or "UP" and "DOWN" for everything else.
* `proxy` - value of the `p2name` field.
* `tunnel` - name of the tunnel this proxy belongs to.

And for each tunnel we also want a `tunnel` dimension with the tunnel's `name`.

Events:

* Info event `Small outgoing traffic!` if outgoing traffic on tunnel is less than 80 bytes.
* Custom alert event `Proxy my_proxy is slow!` if the proxy is up but its outgoing traffic is less than 10 bytes.

**AND we want our code to complain or throw exceptions if the incoming data is invalid!**

Imagine the sheer amount of code and validation required to implement all of the requirements above!

### Implementation

Here is how you could define a nested model that can be evaluated both for metrics and events in just about 80 lines.
The example intentionally uses as much variation as possible to demonstrate the flexibility of the library.

```python
from dynatrace_extension_models import Field, MetricInfo, EventInfo, IngestBase, MetricType, DtEventType


class TunnelProxy(IngestBase):
    p2name: str = Field(...)
    status: str = Field("unknown")
    incoming_bytes: int | None = Field(None, title="incoming_bytes")
    outgoing_bytes: int | None = Field(None, title="outgoing_bytes")

    def properties(self) -> dict:
        return {
            "proxy": self.p2name,
            "status": self.status.upper(),
            "tunnel": getattr(self._parent, "name"),
        }
    
    def status_to_metric(self) -> float:
        return 1 if self.status.upper() == "UP" else 0
    
    def proxy_is_slow_title(self) -> str:
        return f"Proxy {self.p2name} is slow!"

    _metrics = [
        MetricInfo(
            key="fortigate.tunnel.proxy.status",
            properties=properties,
            value=status_to_metric,
        ),
        MetricInfo(
            key="fortigate.tunnel.proxy.bytes.in.count",
            type=MetricType.COUNT,
            properties=properties,
            value=incoming_bytes,
        ),
        MetricInfo(
            key="fortigate.tunnel.proxy.bytes.out.count",
            type=MetricType.COUNT,
            properties=properties,
            value=outgoing_bytes,
        )
    ]

    _events = [
        EventInfo(
            title=proxy_is_slow_title,
            properties=properties,
            type=DtEventType.CUSTOM_ALERT,
            when=lambda v: v.status.upper() == "UP" and v.outgoing_bytes < 10,
        )
    ]


class Tunnel(IngestBase):
    name: str = Field(...)
    incoming_bytes: int | None = Field(None, title="incoming_bytes")
    outgoing_bytes: int | None = Field(None, title="outgoing_bytes")
    proxyid: list[TunnelProxy] | None = Field(None)

    def not_enough_traffic(self) -> bool:
        return self.outgoing_bytes < 80

    def current_incoming_bytes(self) -> int | None:
        return self.incoming_bytes

    _metrics = [
        MetricInfo(
            key="fortigate.tunnel.bytes.in.count",
            type=MetricType.COUNT,
            properties={"tunnel": "{name}"},
            value=current_incoming_bytes,
        ),
        MetricInfo(
            key="fortigate.tunnel.bytes.out.count",
            type=MetricType.COUNT,
            properties={"tunnel": "{name}"},
            value=outgoing_bytes,
        )
    ]

    _events = [
        EventInfo(
            title="Small outgoing traffic!",
            type=DtEventType.CUSTOM_INFO,
            when=not_enough_traffic,
        )
    ]
```

### Results

If you initialize the `Tunnel` model instance with the JSON above and convert it to metrics and events, here is what you would get.

```python
import requests

data = requests.get("https://some-api.com").json()

tunnel = Tunnel(**data)
print(tunnel.mint_lines)
print(tunnel.event_dicts)
```

output:

```text
fortigate.tunnel.bytes.out.count,tunnel="my_tunnel" count,5 1719449431472
fortigate.tunnel.proxy.bytes.in.count,proxy="my_proxy",status="UP",tunnel="my_tunnel" count,3 1719449431472
fortigate.tunnel.proxy.bytes.out.count,proxy="my_proxy",status="UP",tunnel="my_tunnel" count,2 1719449431472
fortigate.tunnel.proxy.status,proxy="my_proxy",status="UP",tunnel="my_tunnel" gauge,1 1719449431472
{'title': 'Proxy my_proxy is slow!', 'event_type': <DtEventType.CUSTOM_ALERT: 'CUSTOM_ALERT'>, 'timeout': 15, 'properties': {'proxy': 'my_proxy', 'status': 'UP', 'tunnel': 'my_tunnel'}}
{'title': 'Small outgoing traffic!', 'event_type': <DtEventType.CUSTOM_INFO: 'CUSTOM_INFO'>, 'timeout': 15}
```

### Ingesting metrics and sending events in Python EF2 framework

Continuing the code above, inside your Python EF2 Dynatrace extension you would do the following:

```python
import requests
from dynatrace_extension import Extension, Status, StatusValue


class ExtensionImpl(Extension):
    def query(self) -> None:
        data = requests.get("https://some-api.com").json()
        tunnel = Tunnel(**data)

        # Ingest metrics
        self.report_mint_lines(tunnel.mint_lines)

        # Ingest events
        for event in tunnel.event_dicts:
          self.report_dt_event_dict(event)
```

🤩 Beautiful!
