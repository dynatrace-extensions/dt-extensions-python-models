from datetime import datetime
from copy import deepcopy
from typing import Any, Callable

from dynatrace_extension import Metric, MetricType
from pydantic import BaseModel

from .metric_info import MetricInfo


def _compute_dimensions(
    dimensions_definition: Callable | list | None = None,
    parent_dimensions: dict[str, str] = None,
    parent: BaseModel | None = None,
) -> dict[str, str]:
    dimensions = {}
    if parent_dimensions:
        dimensions = deepcopy(parent_dimensions)
    if isinstance(parent, BaseModel):
        if isinstance(dimensions_definition, Callable):
            computed_dims = dimensions_definition(parent)
            for d, dim_value in computed_dims.items():
                if dim_value is not None:
                    dimensions[d] = str(dim_value)
        elif isinstance(dimensions_definition, list):
            for d in dimensions_definition:
                dim_value = getattr(parent, d, None)
                if dim_value is not None:
                    dimensions[d] = str(dim_value)
    return dimensions


def _to_metrics(
    data: Any,
    metric_info: MetricInfo | None = None,
    parent: BaseModel | None = None,
    parent_dimensions: dict[str, str] | None = None,
    timestamp: datetime | None = None,
) -> list[Metric]:
    """Turn any type of data into a list of Metric objects by traversing it recursively.
    """
    metrics: list[Metric] = []
            
    # Compute dimensions for this field
    ignore_parent_dimensions = getattr(metric_info, "ignore_parent_dimensions", False)
    dimensions = _compute_dimensions(
        dimensions_definition=getattr(metric_info, "dimensions", None),
        parent_dimensions=None if ignore_parent_dimensions else parent_dimensions,
        parent=parent,
    )

    if isinstance(data, BaseModel):
        # Case 1: BaseModel
        # BaseModel needs to be parsed into individual fields, which in turn,
        # each, can be transformed into a MINT line.
        for field_name, field_info in data.model_fields.items():
            # Retrieve MetricInfo for this field, if it was defined by defining the field
            # through MetricField function.
            metric_info: MetricInfo | None = None
            if isinstance(field_info.json_schema_extra, dict):
                if metric_info_definition := field_info.json_schema_extra.get("metric_info"):
                    metric_info = metric_info_definition
                
            # Retrieve the actual value of the field.
            field_value = getattr(data, field_name, None)

            # If metric key was skipped, use the field name as the key.
            if metric_info and metric_info.key is None:
                metric_info.key = field_name

            field_metrics = _to_metrics(field_value, metric_info, data, dimensions)
            metrics.extend(field_metrics)

    elif isinstance(data, dict):
        # Case 2: Dict
        for item in data.values():
            dict_item_metrics = _to_metrics(item, metric_info, parent, dimensions)
            metrics.extend(dict_item_metrics)

    elif (
        isinstance(data, list)
        or isinstance(data, tuple)
        or isinstance(data, set)
    ):
        # Case 3: List
        for item in data:
            list_item_metrics = _to_metrics(item, metric_info, parent, dimensions)
            metrics.extend(list_item_metrics)

    else:
        # Case 4: Any other data, if it comes with MetricInfo

        # Skip plain fields for which MetricInfo is not specified
        if not isinstance(metric_info, MetricInfo):
            return metrics

        # Do not process metrics without value
        if metric_info.value_factory is None and data is None:
            return metrics

        # Compute value for the metric
        value: float | None = None
        if metric_info.value_factory:
            # If value() function is defined in MetricInfo of this field,
            # then compute the value
            value = metric_info.value_factory(parent)
        else:
            value = data

        # If computed value is None, do not report it
        if value is None:
            return metrics

        if metric_info.type == MetricType.COUNT and timestamp is None:
            timestamp = datetime.now()

        metric = Metric(
            key=metric_info.key,
            value=value,
            dimensions=dimensions,
            metric_type=metric_info.type,
            timestamp=timestamp,
        )
        metrics.append(metric)

    return metrics


class MetricBaseModel(BaseModel):
    """Base class for models that can be converted to MINT lines."""

    def to_metrics(self) -> list[Metric]:
        """Traverse the model recursively and produce list of Metrics"""
        return _to_metrics(self)

    def to_mint_lines(self) -> list[str]:
        """Traverse the model recursively and produce MINT lines."""
        metrics = self.to_metrics()
        return [m.to_mint_line() for m in metrics]
