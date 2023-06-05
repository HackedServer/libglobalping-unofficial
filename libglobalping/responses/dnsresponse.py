from dataclasses import dataclass
from typing import Any

from libglobalping.common import GlobalpingBaseResponse, ResultProbe


@dataclass
class DNSAnswers:
    name: str
    type: str
    ttl: int
    value: str
    dnsclass: str  # API returns "class", which is reserved in Python.

    @classmethod
    def from_api_response(cls, data: dict[str, Any]) -> "DNSAnswers":
        return cls(
            name=data["name"],
            type=data["type"],
            ttl=data["ttl"],
            value=data["value"],
            dnsclass=data["class"],
        )


@dataclass
class DNSTimings:
    total: float


@dataclass
class DNSResult:
    resolver: str
    answers: list[DNSAnswers]
    timings: DNSTimings
    rawOutput: str
    statusCode: int
    statusCodeName: str

    @classmethod
    def from_api_response(cls, data: dict[Any, Any]) -> "DNSResult":
        return cls(
            rawOutput=data["rawOutput"],
            resolver=data["resolver"],
            statusCode=int(data["statusCode"]),
            statusCodeName=data["statusCodeName"],
            answers=[
                DNSAnswers.from_api_response(answer) for answer in data["answers"]
            ],
            timings=DNSTimings(total=float(data["timings"]["total"])),
        )


@dataclass
class DNSResults:
    probe: ResultProbe
    result: DNSResult

    @classmethod
    def from_api_response(cls, data: dict[Any, Any]) -> "DNSResults":
        return cls(
            probe=ResultProbe.from_api_response(data["probe"]),
            result=DNSResult.from_api_response(data["result"]),
        )


@dataclass
class DNSResponse(GlobalpingBaseResponse):
    results: list[DNSResults]

    @classmethod
    def from_api_response(cls, data: dict[Any, Any]) -> "DNSResponse":
        return cls(
            id=data["id"],
            type=data["type"],
            status=data["status"],
            createdAt=data["createdAt"],
            updatedAt=data["updatedAt"],
            probesCount=data["probesCount"],
            results=[DNSResults.from_api_response(r) for r in data["results"]],
        )
