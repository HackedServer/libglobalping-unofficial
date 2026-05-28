"""Exceptions for the GlobalPing API client."""



class GlobalpingError(Exception):
    """Base exception for GlobalPing API errors."""

    def __init__(self, message: str, error_type: str | None = None):
        self.error_type = error_type
        super().__init__(message)


class ValidationError(GlobalpingError):
    """Raised on 400 Bad Request (malformed parameters)."""

    def __init__(self, message: str, params: dict[str, str] | None = None):
        self.params = params
        super().__init__(message, error_type="validation_error")


class NoProbesFoundError(GlobalpingError):
    """Raised on 422 when no suitable probes are available."""

    def __init__(self, message: str = "No matching probes available."):
        super().__init__(message, error_type="no_probes_found")


class RateLimitExceededError(GlobalpingError):
    """Raised on 429 when rate limit is exceeded."""

    def __init__(
        self,
        message: str = "API rate limit exceeded.",
        limit: int | None = None,
        remaining: int | None = None,
        reset: int | None = None,
    ):
        self.limit = limit
        self.remaining = remaining
        self.reset = reset
        super().__init__(message, error_type="rate_limit_exceeded")


class MeasurementTimeoutError(GlobalpingError):
    """Raised when polling for measurement results times out."""

    def __init__(self, measurement_id: str):
        self.measurement_id = measurement_id
        super().__init__(
            f"Measurement {measurement_id} did not complete within the timeout period."
        )
