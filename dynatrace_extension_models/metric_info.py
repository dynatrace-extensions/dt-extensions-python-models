from typing import Callable

from dynatrace_extension import MetricType
from pydantic import BaseModel


ValueFactory = Callable[[BaseModel], float | None]
Dimensions = Callable[[BaseModel], dict] | list[str]
"""Dimensions specified as a computable dict or as a list of model attributes.

Computable dimensions specified as a callable:
    lambda model: {"interface": model.name, "status": model.status.upper()}

Static list of model attributes to be used as dimensions:
    ["name", "status"]
"""


class MetricInfo(BaseModel):
    key: str | None = None
    type: MetricType = MetricType.GAUGE
    value_factory: ValueFactory | None = None
    dimensions: Dimensions | None = None
    ignore_parent_dimensions: bool | None = None