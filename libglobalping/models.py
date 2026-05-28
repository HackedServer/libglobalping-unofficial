"""Pydantic models for GlobalPing API responses."""

from typing import Any, Literal

from pydantic import BaseModel, Field


# --- Shared / Probe models ---


class ProbeLocation(BaseModel):
    continent: str
    region: str
    country: str
    state: str | None = None
    city: str
    asn: int
    network: str
    latitude: float
    longitude: float


class Probe(BaseModel):
    version: str
    location: ProbeLocation
    tags: list[str] = []
    resolvers: list[str] = []


# --- Measurement result probe (includes tags/resolvers) ---


class ResultProbe(BaseModel):
    continent: str
    region: str
    country: str
    state: str | None = None
    city: str
    asn: int
    network: str
    latitude: float
    longitude: float
    tags: list[str] = []
    resolvers: list[str] = []


# --- Location options for creating measurements ---


class MeasurementLocation(BaseModel):
    continent: str | None = None
    region: str | None = None
    country: str | None = None
    state: str | None = None
    city: str | None = None
    asn: int | None = None
    network: str | None = None
    tags: list[str] | None = None
    magic: str | None = None
    limit: int | None = None


# --- Ping ---


class PingStats(BaseModel):
    min: float | None = None
    max: float | None = None
    avg: float | None = None
    total: int
    rcv: int
    drop: int
    loss: float


class PingTiming(BaseModel):
    rtt: float
    ttl: float | None = None


class PingResult(BaseModel):
    status: str
    raw_output: str = Field(alias="rawOutput")
    resolved_address: str | None = Field(None, alias="resolvedAddress")
    resolved_hostname: str | None = Field(None, alias="resolvedHostname")
    timings: list[PingTiming] = []
    stats: PingStats | None = None

    model_config = {"populate_by_name": True}


class PingResultItem(BaseModel):
    probe: ResultProbe
    result: PingResult


class PingResponse(BaseModel):
    id: str
    type: Literal["ping"]
    status: str
    created_at: str = Field(alias="createdAt")
    updated_at: str = Field(alias="updatedAt")
    target: str | None = None
    probes_count: int = Field(alias="probesCount")
    results: list[PingResultItem] = []

    model_config = {"populate_by_name": True}


# --- Traceroute ---


class TracerouteHopTiming(BaseModel):
    rtt: float


class TracerouteHop(BaseModel):
    resolved_address: str | None = Field(None, alias="resolvedAddress")
    resolved_hostname: str | None = Field(None, alias="resolvedHostname")
    timings: list[TracerouteHopTiming] = []

    model_config = {"populate_by_name": True}


class TracerouteResult(BaseModel):
    status: str
    raw_output: str = Field(alias="rawOutput")
    resolved_address: str | None = Field(None, alias="resolvedAddress")
    resolved_hostname: str | None = Field(None, alias="resolvedHostname")
    hops: list[TracerouteHop] = []

    model_config = {"populate_by_name": True}


class TracerouteResultItem(BaseModel):
    probe: ResultProbe
    result: TracerouteResult


class TracerouteResponse(BaseModel):
    id: str
    type: Literal["traceroute"]
    status: str
    created_at: str = Field(alias="createdAt")
    updated_at: str = Field(alias="updatedAt")
    target: str | None = None
    probes_count: int = Field(alias="probesCount")
    results: list[TracerouteResultItem] = []

    model_config = {"populate_by_name": True}


# --- DNS ---


class DNSAnswer(BaseModel):
    name: str
    type: str
    ttl: int
    class_: str = Field(alias="class")
    value: str

    model_config = {"populate_by_name": True}


class DNSTimings(BaseModel):
    total: float


class DNSHopResult(BaseModel):
    resolver: str
    answers: list[DNSAnswer] = []
    timings: DNSTimings


class DNSResult(BaseModel):
    status: str
    raw_output: str = Field(alias="rawOutput")
    status_code: int | None = Field(None, alias="statusCode")
    status_code_name: str | None = Field(None, alias="statusCodeName")
    resolver: str | None = None
    answers: list[DNSAnswer] = []
    timings: DNSTimings | None = None
    hops: list[DNSHopResult] | None = None

    model_config = {"populate_by_name": True}


class DNSResultItem(BaseModel):
    probe: ResultProbe
    result: DNSResult


class DNSResponse(BaseModel):
    id: str
    type: Literal["dns"]
    status: str
    created_at: str = Field(alias="createdAt")
    updated_at: str = Field(alias="updatedAt")
    target: str | None = None
    probes_count: int = Field(alias="probesCount")
    results: list[DNSResultItem] = []

    model_config = {"populate_by_name": True}


# --- MTR ---


class MTRStats(BaseModel):
    min: float
    max: float
    avg: float
    total: int
    rcv: int
    drop: int
    loss: float
    st_dev: float = Field(alias="stDev")
    j_min: float = Field(alias="jMin")
    j_max: float = Field(alias="jMax")
    j_avg: float = Field(alias="jAvg")

    model_config = {"populate_by_name": True}


class MTRTiming(BaseModel):
    rtt: float


class MTRHop(BaseModel):
    resolved_address: str | None = Field(None, alias="resolvedAddress")
    resolved_hostname: str | None = Field(None, alias="resolvedHostname")
    asn: list[int] = []
    timings: list[MTRTiming] = []
    stats: MTRStats

    model_config = {"populate_by_name": True}


class MTRResult(BaseModel):
    status: str
    raw_output: str = Field(alias="rawOutput")
    resolved_address: str | None = Field(None, alias="resolvedAddress")
    resolved_hostname: str | None = Field(None, alias="resolvedHostname")
    hops: list[MTRHop] = []

    model_config = {"populate_by_name": True}


class MTRResultItem(BaseModel):
    probe: ResultProbe
    result: MTRResult

    def pretty_print(self, line_length: int = 100) -> str:
        lines: list[str] = []
        for hop in self.result.hops:
            hostname = hop.resolved_hostname or hop.resolved_address or "UNKNOWN"
            timings = [
                f"{t.rtt}ms".ljust(10) if t.rtt else "*".center(10)
                for t in hop.timings
            ]
            line = "{}{}".format(
                hostname[: line_length - 34 - 2].ljust(line_length - 34),
                "- ".join(timings),
            )
            lines.append(line)
        output = "\n".join(lines)
        print(output)
        return output


class MTRResponse(BaseModel):
    id: str
    type: Literal["mtr"]
    status: str
    created_at: str = Field(alias="createdAt")
    updated_at: str = Field(alias="updatedAt")
    target: str | None = None
    probes_count: int = Field(alias="probesCount")
    results: list[MTRResultItem] = []

    model_config = {"populate_by_name": True}


# --- HTTP ---


class HTTPTimings(BaseModel):
    total: int | None = None
    download: int | None = None
    first_byte: int | None = Field(None, alias="firstByte")
    dns: int | None = None
    tls: int | None = None
    tcp: int | None = None

    model_config = {"populate_by_name": True}


class TLSCertificateSubject(BaseModel):
    CN: str | None = None
    alt: str | None = None


class TLSCertificateIssuer(BaseModel):
    C: str | None = None
    O: str | None = None
    CN: str | None = None


class TLSCertificate(BaseModel):
    protocol: str | None = None
    cipher_name: str | None = Field(None, alias="cipherName")
    authorized: bool | None = None
    error: str | None = None
    created_at: str | None = Field(None, alias="createdAt")
    expires_at: str | None = Field(None, alias="expiresAt")
    subject: TLSCertificateSubject | None = None
    issuer: TLSCertificateIssuer | None = None
    key_type: str | None = Field(None, alias="keyType")
    key_bits: int | None = Field(None, alias="keyBits")
    serial_number: str | None = Field(None, alias="serialNumber")
    fingerprint256: str | None = None
    public_key: str | None = Field(None, alias="publicKey")

    model_config = {"populate_by_name": True}


class HTTPResult(BaseModel):
    status: str
    raw_output: str = Field(alias="rawOutput")
    resolved_address: str | None = Field(None, alias="resolvedAddress")
    headers: dict[str, Any] | None = None
    raw_headers: str | None = Field(None, alias="rawHeaders")
    raw_body: str | None = Field(None, alias="rawBody")
    truncated: bool | None = None
    status_code: int | None = Field(None, alias="statusCode")
    status_code_name: str | None = Field(None, alias="statusCodeName")
    timings: HTTPTimings | None = None
    tls: TLSCertificate | None = None

    model_config = {"populate_by_name": True}


class HTTPResultItem(BaseModel):
    probe: ResultProbe
    result: HTTPResult


class HTTPResponse(BaseModel):
    id: str
    type: Literal["http"]
    status: str
    created_at: str = Field(alias="createdAt")
    updated_at: str = Field(alias="updatedAt")
    target: str | None = None
    probes_count: int = Field(alias="probesCount")
    results: list[HTTPResultItem] = []

    model_config = {"populate_by_name": True}


# --- Generic measurement response (for raw access) ---


class MeasurementResponse(BaseModel):
    id: str
    type: str
    status: str
    created_at: str = Field(alias="createdAt")
    updated_at: str = Field(alias="updatedAt")
    target: str | None = None
    probes_count: int = Field(alias="probesCount")
    results: list[dict[str, Any]] = []

    model_config = {"populate_by_name": True}


# --- Rate limits ---


class RateLimitDetail(BaseModel):
    type: str
    limit: int
    remaining: int
    reset: int


class RateLimitMeasurements(BaseModel):
    create: RateLimitDetail


class RateLimit(BaseModel):
    measurements: RateLimitMeasurements


class Credits(BaseModel):
    remaining: int


class Limits(BaseModel):
    rate_limit: RateLimit = Field(alias="rateLimit")
    credits: Credits | None = None

    model_config = {"populate_by_name": True}
