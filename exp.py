from pydantic import BaseModel, Field, PrivateAttr
from typing import Callable


class MetricInfo(BaseModel):
    key: str = Field(...)
    when: Callable | None = Field(None)
    value: float | None = Field(None)


class IngestBase(BaseModel):
    _metrics: list[MetricInfo] = PrivateAttr([])


class Foo(IngestBase):
    name: str = Field(...)

    def bar(self):
        print(f"Estimating: {self.name}")
        return len(self.name) > 4
    
    _metrics = [
        MetricInfo(
            key="{name}",
            when=bar,
        )
    ]


if __name__ == "__main__":
    f = Foo(name="bar")
    print(f.model_dump())
    print(f._metrics)
    print(f._metrics[0].when(f))
