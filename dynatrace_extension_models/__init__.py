from datetime import datetime
from copy import deepcopy
from typing import Any, Callable

from dynatrace_extension import Metric, MetricType, DtEventType, Severity, SummaryStat
from pydantic import BaseModel, ConfigDict, Field, PrivateAttr
from pydantic.fields import FieldInfo


Properties = Callable[[BaseModel], dict] | list[str] | dict[str, str]
"""Properties (dimensions) to be used with an event, metric, or log line.

Can be specified as either:

1. Computable properties specified as a callable that receives an instance
   of the entire model (most flexible option):

   lambda model: {"interface": model.name, "status": model.status.upper()}

2. Static list of model field names to be used as properties (shortest
   option):

   ["name", "status"]

3. Static dict where key is the resulting property name and value is the
   name of the field who's value is going to be used as a property value.
   The value must be formatted as a str.format().

   {"instance_name": "{name}", "state": "{status}"}
"""


class Event:
    def __init__(
        self,
        title: str,
        event_type: DtEventType,
        start_time: int | None = None,
        end_time: int | None = None,
        timeout: int | None = None,
        entity_selector: str | None = None,
        properties: dict[str, str] | None = None,
    ) -> None:
        self.title = title
        self.event_type = event_type
        self.start_time = start_time
        self.end_time = end_time
        self.timeout = timeout
        self.entity_selector = entity_selector
        self.properties = properties

    def to_dict(self) -> dict:
        result = {
            "title": self.title,
            "event_type": self.event_type,
        }

        if self.start_time:
            result["start_time"] = self.start_time
        if self.end_time:
            result["end_time"] = self.end_time
        if self.timeout:
            result["timeout"] = self.timeout
        if self.entity_selector:
            result["entity_selector"] = self.entity_selector
        if self.properties:
            result["properties"] = self.properties
        
        return result


class Log:
    def __init__(
        self,
        content: str,
        severity: Severity | None = None,
        properties: dict[str, str] | None = None,
    ) -> None:
        self.content = content
        self.severity = severity
        self.properties = properties


class IngestableInfo(BaseModel):
    properties: Properties | None = Field(None)
    when: Callable[[BaseModel], bool] | bool | None = Field(None)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def _evaluate_properties(self, model: BaseModel):
        dimensions = {}
        if isinstance(self.properties, Callable):
            computed_dims = self.properties(model)
            for d, dim_value in computed_dims.items():
                if dim_value is not None:
                    dimensions[d] = str(dim_value)
        elif isinstance(self.properties, list):
            if len(self.properties):
                for d in self.properties:
                    dim_value = getattr(model, d, None)
                    if dim_value is not None:
                        dimensions[d] = str(dim_value)
        elif isinstance(self.properties, dict):
            if len(self.properties):
                for d, dim_ref in self.properties.items():
                    dim_value = dim_ref.format(**model.model_dump())
                    if dim_value is not None:
                        dimensions[d] = str(dim_value)
        return dimensions


class MetricInfo(IngestableInfo):
    key: str = Field(...)
    type: MetricType = Field(MetricType.GAUGE)
    value: Callable[[BaseModel], float | int | str | SummaryStat] | float | int | str | SummaryStat | FieldInfo | None = Field(None)

    def _evaluate(self, model: BaseModel, timestamp: datetime | None = None) -> Metric | None:
        # Decide whether we should evaluate
        if self.when is None:
            # If "when" is not set, consider it True by default
            pass
        elif isinstance(self.when, Callable):
            evaluated_when = self.when(model)
            if not evaluated_when:
                return None
        elif isinstance(self.when, bool):
            if not self.when:
                return None

        # Evaluate value
        evaluated_value: float | int | str | SummaryStat | None = None
        if isinstance(self.value, Callable):
            evaluated_value = self.value(model)
        # This works in such a weird way because comparing two FieldInfo objects doesn't work.
        # FieldInfo object has no reference to the field name it defines. We have to use title.
        elif isinstance(self.value, FieldInfo):
            for field_name, field_info in model.model_fields.items():
                if (
                    field_info.title
                    and self.value.title
                    and field_info.title == self.value.title
                ):
                    evaluated_value = getattr(model, field_name, None)
                    break
        elif self.value is not None:
            evaluated_value = f"{self.value}"

        # We can't ingest a metric with value of None
        if evaluated_value is None:
            return None

        # Evaluate properties
        evaluated_properties = self._evaluate_properties(model)

        # Make sure timestamp is set for COUNT metrics
        if self.type == MetricType.COUNT and timestamp is None:
            timestamp = datetime.now()

        # Compose the Metric object
        metric = Metric(
            key=self.key,
            value=evaluated_value,
            dimensions=evaluated_properties,
            metric_type=self.type,
            timestamp=timestamp,
        )

        return metric


class EventInfo(IngestableInfo):
    title: Callable[[BaseModel], str] | str = Field(...)
    type: DtEventType = Field(DtEventType.CUSTOM_ALERT)
    timeout: Callable[[BaseModel], int] | int | None = Field(None)
    entity_selector:  Callable[[BaseModel], str] | str | None = Field(None)

    def _evaluate(self, model: BaseModel) -> Event | None:
        # Decide whether we should evaluate
        if self.when is None:
            return None
        elif isinstance(self.when, Callable):
            evaluated_when = self.when(model)
            if not evaluated_when:
                return None
        elif isinstance(self.when, bool):
            if not self.when:
                return None

        # Evaluate title
        evaluated_title: str | None = None
        if isinstance(self.title, Callable):
            evaluated_title = self.title(model)
        elif self.title is not None:
            evaluated_title = self.title

        # Evaluate timeout
        evaluated_timeout: int | None = None
        if isinstance(self.timeout, Callable):
            evaluated_timeout = self.timeout(model)
        elif self.timeout is not None:
            evaluated_timeout = int(self.timeout)

        # Evaluate entity selector
        evaluated_entity_selector: str | None = None
        if isinstance(self.entity_selector, Callable):
            evaluated_entity_selector = self.entity_selector(model)
        elif self.entity_selector is not None:
            evaluated_entity_selector = f"{self.entity_selector}"

        # We can't ingest an event without a title
        if evaluated_title is None:
            return None

        # Evaluate properties
        evaluated_properties = self._evaluate_properties(model)

        # Compose the Event object
        event = Event(
            title=evaluated_title,
            event_type=self.type,
            timeout=evaluated_timeout,
            entity_selector=evaluated_entity_selector,
            properties=evaluated_properties,
        )

        return event
        

class LogInfo(IngestableInfo):
    content: str | None = Field(None)
    timestamp: datetime | None = Field(None)
    severity: Severity | None = Field(None)


class EvaluationResult:
    def __init__(self) -> None:
        self.metrics: list[Metric] = []
        self.events: list[Event] = []
        self.logs: list[Log] = []

    def append(self, other: "EvaluationResult") -> None:
        """Append another EvaluationResult to the current one."""
        self.metrics.extend(other.metrics)
        self.events.extend(other.events)
        self.logs.extend(other.logs)


class _IngestBase(BaseModel):
    """Private base class for models that can be converted to Metrics, Events, or Log lines."""

    _metrics: list[MetricInfo] = PrivateAttr([])
    _events: list[EventInfo] = PrivateAttr([])
    _logs: list[LogInfo] = PrivateAttr([])
    _parent: BaseModel | None = PrivateAttr(None)

    _evaluation_result: EvaluationResult | None = PrivateAttr(None)
    
    model_config = ConfigDict(
        use_enum_values=True,
        validate_default=True,
        arbitrary_types_allowed=True,
    )


def _evaluate(
    data: Any,
    parent: BaseModel | None = None,
    timestamp: datetime | None = None,
) -> EvaluationResult:
    """Recursively evaluate the model to compute its metrics, events, and logs.
    
    Args:
        data (Any): BaseModel or individual fields to evaluate.
        parent (BaseModel): Parent model of this field if it exists.
        timestamp (datetime): Timestamp to use for evaluation result.
    """

    evaluation_result = EvaluationResult()

    if isinstance(data, BaseModel):
        # Only perform the evaluation on IngestBase objects
        if isinstance(data, _IngestBase):
            # If the parent is provided, pass it down to data obect
            if parent:
                data._parent = parent
            
            # Evaluate metrics
            for metric_info in data._metrics:
                evaluated_metric = metric_info._evaluate(data, timestamp)
                if evaluated_metric is not None:
                    evaluation_result.metrics.append(evaluated_metric)

            # Evaluate events
            for event_info in data._events:
                evaluated_event = event_info._evaluate(data)
                if evaluated_event is not None:
                    evaluation_result.events.append(evaluated_event)

        # Go through all child fields
        for field_name, field_info in data.model_fields.items():
            field_value = getattr(data, field_name, None)
            evaluated_field = _evaluate(field_value, data, timestamp)
            evaluation_result.append(evaluated_field)

    elif isinstance(data, dict):
        for dict_item in data.values():
            evaluated_dict_item = _evaluate(dict_item, parent, timestamp)
            evaluation_result.append(evaluated_dict_item)

    elif (
        isinstance(data, list)
        or isinstance(data, tuple)
        or isinstance(data, set)
    ):
        for list_item in data:
            evaluated_list_item = _evaluate(list_item, parent, timestamp)
            evaluation_result.append(evaluated_list_item)

    return evaluation_result


class IngestBase(_IngestBase):
    """Base class for models that can be converted to Metrics, Events, or Log lines."""

    def evaluate(self, timestamp: datetime | None = None) -> EvaluationResult:
        """Evaluate the model recursively and comput metrics, events, and logs."""
        if timestamp is None:
            timestamp = datetime.now()
        self._evaluation_result = _evaluate(self, None, timestamp)
        return self._evaluation_result

    @property
    def metrics(self) -> list[Metric]:
        """Return all evaluated metrics."""
        if self._evaluation_result is None:
            self.evaluate()
        return self._evaluation_result.metrics

    @property
    def mint_lines(self) -> list[str]:
        """Return all evaluated metrics as MINT lines."""
        return [m.to_mint_line() for m in self.metrics]

    @property
    def events(self) -> list[Event]:
        """Return all evaluated events."""
        if self._evaluation_result is None:
            self.evaluate()
        return self._evaluation_result.events
    
    @property
    def event_dicts(self) -> list[dict]:
        """Return all evaluated events as dicts."""
        return [e.to_dict() for e in self.events]
    