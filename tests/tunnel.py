from dynatrace_extension_models import Field, MetricField, MetricBaseModel, MetricType
from .tunnel_proxy import TunnelProxy


class Tunnel(MetricBaseModel):
    name: str = Field(...)
    incoming_bytes: int | None = MetricField(
        None,
        key="fortigate.tunnel.bytes.in.count",
        type=MetricType.COUNT,
        dimensions=lambda v: {"tunnel": v.name},
    )
    outgoing_bytes: int | None = MetricField(
        None,
        key="fortigate.tunnel.bytes.out.count",
        type=MetricType.COUNT,
        dimensions=lambda v: {"tunnel": v.name},
    )
    proxyid: list[TunnelProxy] | None = MetricField(
        None,
        dimensions=lambda v: {"tunnel": v.name},
    )


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
