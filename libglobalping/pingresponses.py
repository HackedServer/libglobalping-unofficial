from dataclasses import dataclass
from typing import Any

from libglobalping.common import GlobalpingBaseResponse, ResultProbe


@dataclass
class PINGStats:
    min: float
    max: float
    avg: float
    loss: float

    @classmethod
    def from_api_response(cls, data: dict[str, float]) -> "PINGStats":
        return cls(**data)


@dataclass
class PINGResult:
    rawOutput: str
    resolvedAddress: str
    resolvedHostname: str
    timings: list
    stats: PINGStats

    @classmethod
    def from_api_response(cls, data: dict[Any, Any]) -> "PINGResults":
        return cls(
            rawOutput=data["rawOutput"],
            resolvedAddress=data["resolvedAddress"],
            resolvedHostname=data["resolvedHostname"],
            timings=data["timings"],
            stats=PINGStats.from_api_response(data["stats"]),
        )


@dataclass
class PINGResults:
    probe: ResultProbe
    result: PINGResult

    @classmethod
    def from_api_response(cls, data: dict[Any, Any]) -> "PINGResults":
        return cls(
            probe=ResultProbe.from_api_response(data["probe"]),
            result=PINGResult.from_api_response(data["result"]),
        )


@dataclass
class PINGResponse(GlobalpingBaseResponse):
    results: list[PINGResults]

    @classmethod
    def from_api_response(cls, data: dict[Any, Any]) -> "PINGResponse":

        return cls(
            id=data["id"],
            type=data["type"],
            status=data["status"],
            createdAt=data["createdAt"],
            updatedAt=data["updatedAt"],
            probesCount=data["probesCount"],
            results=[PINGResults.from_api_response(r) for r in data["results"]],
        )
