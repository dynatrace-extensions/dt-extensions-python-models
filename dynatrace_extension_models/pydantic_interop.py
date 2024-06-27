# import typing
# from typing import Any, Literal

# from pydantic import Field, AliasChoices, AliasPath
# from pydantic.fields import _Unset, Deprecated, JsonDict
# from pydantic.types import Discriminator
# from pydantic_core import PydanticUndefined

# from .models import MetricInfo, EventInfo, LogInfo


# def IngestField(
#     default: Any = PydanticUndefined,
#     *,
#     metrics: list[MetricInfo] | None = _Unset,
#     events: list[EventInfo] | None = _Unset,
#     logs: list[LogInfo] | None = _Unset,
#     default_factory: typing.Callable[[], Any] | None = _Unset,
#     alias: str | None = _Unset,
#     alias_priority: int | None = _Unset,
#     validation_alias: str | AliasPath | AliasChoices | None = _Unset,
#     serialization_alias: str | None = _Unset,
#     title: str | None = _Unset,
#     description: str | None = _Unset,
#     examples: list[Any] | None = _Unset,
#     exclude: bool | None = _Unset,
#     discriminator: str | Discriminator | None = _Unset,
#     deprecated: Deprecated | str | bool | None = _Unset,
#     json_schema_extra: JsonDict | typing.Callable[[JsonDict], None] | None = _Unset,
#     frozen: bool | None = _Unset,
#     validate_default: bool | None = _Unset,
#     repr: bool = _Unset,
#     init: bool | None = _Unset,
#     init_var: bool | None = _Unset,
#     kw_only: bool | None = _Unset,
#     pattern: str | typing.Pattern[str] | None = _Unset,
#     strict: bool | None = _Unset,
#     coerce_numbers_to_str: bool | None = _Unset,
#     gt: float | None = _Unset,
#     ge: float | None = _Unset,
#     lt: float | None = _Unset,
#     le: float | None = _Unset,
#     multiple_of: float | None = _Unset,
#     allow_inf_nan: bool | None = _Unset,
#     max_digits: int | None = _Unset,
#     decimal_places: int | None = _Unset,
#     min_length: int | None = _Unset,
#     max_length: int | None = _Unset,
#     union_mode: Literal['smart', 'left_to_right'] = _Unset,
# ) -> Any:
#     """Create a field that can be ingested into Dynatrace as Metrics, Events, and Logs.

#     In addition to standard Field functionality in Pydantic you can specify
#     which metrics, events, and logs the field will be converted to.

#     Note:
#         - Any `_Unset` objects will be replaced by the corresponding value defined in the `_DefaultValues` dictionary.
#           If a key for the `_Unset` object is not found in the `_DefaultValues` dictionary, it will default to `None`

#     Args:
#         default: Default value if the field is not set.
#         metrics: Metric definitions for this field. For every definition a metric will be generated.
#         events: Event definitions for this field. For every definition an event will be generated.
#         logs: Log definitions for this field. For every definition a log record will be generated.
#         default_factory: A callable to generate the default value, such as :func:`~datetime.utcnow`.
#         alias: The name to use for the attribute when validating or serializing by alias.
#             This is often used for things like converting between snake and camel case.
#         alias_priority: Priority of the alias. This affects whether an alias generator is used.
#         validation_alias: Like `alias`, but only affects validation, not serialization.
#         serialization_alias: Like `alias`, but only affects serialization, not validation.
#         title: Human-readable title.
#         description: Human-readable description.
#         examples: Example values for this field.
#         exclude: Whether to exclude the field from the model serialization.
#         discriminator: Field name or Discriminator for discriminating the type in a tagged union.
#         deprecated: A deprecation message, an instance of `warnings.deprecated` or the `typing_extensions.deprecated` backport,
#             or a boolean. If `True`, a default deprecation message will be emitted when accessing the field.
#         json_schema_extra: A dict or callable to provide extra JSON schema properties.
#         frozen: Whether the field is frozen. If true, attempts to change the value on an instance will raise an error.
#         validate_default: If `True`, apply validation to the default value every time you create an instance.
#             Otherwise, for performance reasons, the default value of the field is trusted and not validated.
#         repr: A boolean indicating whether to include the field in the `__repr__` output.
#         init: Whether the field should be included in the constructor of the dataclass.
#             (Only applies to dataclasses.)
#         init_var: Whether the field should _only_ be included in the constructor of the dataclass.
#             (Only applies to dataclasses.)
#         kw_only: Whether the field should be a keyword-only argument in the constructor of the dataclass.
#             (Only applies to dataclasses.)
#         coerce_numbers_to_str: Whether to enable coercion of any `Number` type to `str` (not applicable in `strict` mode).
#         strict: If `True`, strict validation is applied to the field.
#             See [Strict Mode](../concepts/strict_mode.md) for details.
#         gt: Greater than. If set, value must be greater than this. Only applicable to numbers.
#         ge: Greater than or equal. If set, value must be greater than or equal to this. Only applicable to numbers.
#         lt: Less than. If set, value must be less than this. Only applicable to numbers.
#         le: Less than or equal. If set, value must be less than or equal to this. Only applicable to numbers.
#         multiple_of: Value must be a multiple of this. Only applicable to numbers.
#         min_length: Minimum length for iterables.
#         max_length: Maximum length for iterables.
#         pattern: Pattern for strings (a regular expression).
#         allow_inf_nan: Allow `inf`, `-inf`, `nan`. Only applicable to numbers.
#         max_digits: Maximum number of allow digits for strings.
#         decimal_places: Maximum number of decimal places allowed for numbers.
#         union_mode: The strategy to apply when validating a union. Can be `smart` (the default), or `left_to_right`.
#             See [Union Mode](standard_library_types.md#union-mode) for details.

#     Returns:
#         A new [`FieldInfo`][pydantic.fields.FieldInfo]. The return annotation is `Any` so `Field` can be used on
#             type-annotated fields without causing a type error.
#     """
#     if (
#         metrics == _Unset
#         or not isinstance(metrics, list)
#         or not metrics
#         or any([not isinstance(m, MetricInfo) for m in metrics])
#     ):
#         metrics = None

#     if (
#         events == _Unset
#         or not isinstance(events, list)
#         or not events
#         or any([not isinstance(e, EventInfo) for e in events])
#     ):
#         events = None

#     if (
#         logs == _Unset
#         or not isinstance(logs, list)
#         or not logs
#         or any([not isinstance(l, LogInfo) for l in logs])
#     ):
#         logs = None

#     _json_schema_extra = {
#         "dt_metric_definitions": metrics,
#         "dt_event_definitions": events,
#         "dt_log_definitions": logs,
#     }
#     if json_schema_extra != _Unset and json_schema_extra:
#         _json_schema_extra.update(json_schema_extra)

#     return Field(
#         default=default,
#         default_factory=default_factory,
#         alias=alias,
#         alias_priority=alias_priority,
#         validation_alias=validation_alias,
#         serialization_alias=serialization_alias,
#         title=title,
#         description=description,
#         examples=examples,
#         exclude=exclude,
#         discriminator=discriminator,
#         deprecated=deprecated,
#         json_schema_extra=_json_schema_extra,
#         frozen=frozen,
#         validate_default=validate_default,
#         repr=repr,
#         init=init,
#         init_var=init_var,
#         kw_only=kw_only,
#         pattern=pattern,
#         strict=strict,
#         coerce_numbers_to_str=coerce_numbers_to_str,
#         gt=gt,
#         ge=ge,
#         lt=lt,
#         le=le,
#         multiple_of=multiple_of,
#         allow_inf_nan=allow_inf_nan,
#         max_digits=max_digits,
#         decimal_places=decimal_places,
#         min_length=min_length,
#         max_length=max_length,
#         union_mode=union_mode,
#     )





# def _compute_properties(
#     properties_to_compute: Properties | None = None,
#     parent_properties_to_inherit: dict[str, str] = None,
#     parent: BaseModel | None = None,
# ) -> dict[str, str]:
#     dimensions = {}
#     if parent_properties_to_inherit:
#         dimensions = deepcopy(parent_properties_to_inherit)
#     if isinstance(parent, BaseModel):
#         if isinstance(properties_to_compute, Callable):
#             computed_dims = properties_to_compute(parent)
#             for d, dim_value in computed_dims.items():
#                 if dim_value is not None:
#                     dimensions[d] = str(dim_value)
#         elif isinstance(properties_to_compute, list):
#             if len(properties_to_compute):
#                 first = properties_to_compute[0]
#                 if isinstance(first, str):
#                     for d in properties_to_compute:
#                         dim_value = getattr(parent, d, None)
#                         if dim_value is not None:
#                             dimensions[d] = str(dim_value)
#                 elif isinstance(first, tuple):
#                     for d, alias in properties_to_compute:
#                         dim_value = getattr(parent, d, None)
#                         if dim_value is not None:
#                             dimensions[alias] = str(dim_value)
#     return dimensions


# def _compute(
#     data: Any,
#     parent_metric_definition: MetricInfo | None = None,
#     parent: BaseModel | None = None,
#     parent_properties_to_inherit: dict[str, str] | None = None,
#     timestamp: datetime | None = None,
# ) -> list[Metric]:
#     metrics: list[Metric] = []
            
#     # Compute dimensions for this field
#     ignore_parent_properties = getattr(parent_metric_definition, "ignore_parent_properties", False)
#     properties = _compute_properties(
#         properties_to_compute=getattr(parent_metric_definition, "properties", None),
#         parent_properties_to_inherit=None if ignore_parent_properties else parent_properties_to_inherit,
#         parent=parent,
#     )

#     if isinstance(data, BaseModel):
#         # Case 1: BaseModel
#         # BaseModel needs to be parsed into individual fields, which in turn,
#         # each, can be transformed into a MINT line.
#         for field_name, field_info in data.model_fields.items():
#             # A. Compute metrics

#             # Retrieve MetricInfo definitions for this field
#             metric_definition: MetricInfo | None = None
#             if isinstance(field_info.json_schema_extra, dict):
#                 if metric_info_list := field_info.json_schema_extra.get("dt_metric_definitions"):
#                     metric_definitions = metric_info_list
                
#             # Retrieve the actual value of the field.
#             field_value = getattr(data, field_name, None)

#             # If metric key was skipped for any of defined metrics, then use
#             # the field name as their key.
#             if  and m.key is None:
#                 m.key = field_name
# \
#             field_data_points_for_metric = _compute(field_value, data, dimensions)
#             metrics.extend(field_metrics)

#     elif isinstance(data, dict):
#         # Case 2: Dict
#         for item in data.values():
#             dict_item_metrics = _compute(item, metric_info, parent, dimensions)
#             metrics.extend(dict_item_metrics)

#     elif (
#         isinstance(data, list)
#         or isinstance(data, tuple)
#         or isinstance(data, set)
#     ):
#         # Case 3: List
#         for item in data:
#             list_item_metrics = _compute(item, metric_info, parent, dimensions)
#             metrics.extend(list_item_metrics)

#     else:
#         # Case 4: Any other data, if it comes with MetricInfo

#         # Skip plain fields for which MetricInfo is not specified
#         if not isinstance(metric_info, MetricInfo):
#             return metrics

#         # Do not process metrics without value
#         if metric_info.value_factory is None and data is None:
#             return metrics

#         # Compute value for the metric
#         value: float | None = None
#         if metric_info.value_factory:
#             # If value() function is defined in MetricInfo of this field,
#             # then compute the value
#             value = metric_info.value_factory(parent)
#         else:
#             value = data

#         # If computed value is None, do not report it
#         if value is None:
#             return metrics

#         if metric_info.type == MetricType.COUNT and timestamp is None:
#             timestamp = datetime.now()

#         metric = Metric(
#             key=metric_info.key,
#             value=value,
#             dimensions=dimensions,
#             metric_type=metric_info.type,
#             timestamp=timestamp,
#         )
#         metrics.append(metric)

#     return metrics