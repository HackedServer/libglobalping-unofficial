from functools import cached_property
from typing import Optional

import requests
from .httpresponses import HTTPResponse
from .common import (
    DOMAIN_NAME,
    ApiPath,
    Probe,
    ProbeLocation,
    Probes,
    Schemas,
    Status,
    await_completion,
)


class GlobalpingClient:
    def __init__(self, token: Optional[str] = None):
        super().__init__()
        self.token = token

    @cached_property
    def get_probes(self) -> Probes:
        return Probes.generate()

    def has_country(self, country: str) -> bool:
        return self.get_probes().has_country(country)

    def check_http(self, url: str) -> HTTPResponse:
        """Blocking"""
        body = Schemas.HTTP(url=url)
        query_url = DOMAIN_NAME._replace(path=ApiPath.MEASUREMENTS.value).geturl()
        response = requests.post(query_url, json=body).json()
        request_id = response["id"]
        result = await_completion(request_id=request_id)

        return HTTPResponse.from_api_response(result)
