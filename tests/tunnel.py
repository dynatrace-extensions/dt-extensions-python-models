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

    _metrics = [
        MetricInfo(
            key="fortigate.tunnel.bytes.in.count",
            type=MetricType.COUNT,
            properties={"tunnel": "{name}"},
            value=incoming_bytes,
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


# For proxyid field
# we call _to_mint_lines with
# - list of TunnelProxy objects
# - Tunnel parent object
# - metric_info that wraps the list
# - dimensions which are empty

# For each tunnel proxy in list
# we call _to_mint_lines with
# - actual TunnelProxy object
# - Tunnel parent object
# - metric_info that wraps the list
# - dimensions which are empty

# We process TunnelProxy object
# - wrapped metric_info dimensions are properly computed
# - the rest is normal object 
