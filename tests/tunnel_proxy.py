from dynatrace_extension_models import Field, MetricField, MetricBaseModel, MetricType


class TunnelProxy(MetricBaseModel):
    p2name: str = Field(...)
    status: str = MetricField(
        "unknown",
        key="fortigate.tunnel.proxy.status",
        dimensions=lambda v: {"proxy": v.p2name, "status": v.status.upper()},
        value_factory=lambda v: 1 if v.status.upper() == "UP" else 0,
    )
    incoming_bytes: int | None = MetricField(
        key="fortigate.tunnel.proxy.bytes.in.count",
        type=MetricType.COUNT,
        dimensions=lambda v: {"proxy": v.p2name},
    )
    outgoing_bytes: int | None = MetricField(
        None,
        key="fortigate.tunnel.proxy.bytes.out.count",
        type=MetricType.COUNT,
        dimensions=lambda v: {"proxy": v.p2name},
    )
