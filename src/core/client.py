"""HTTP client for communicating with beat-books-data service."""

import asyncio
import random

import httpx
from typing import Optional, Dict, Any
from fastapi import HTTPException
from src.core.config import settings
from src.core.circuit_breaker import CircuitBreaker

# Status codes that are safe to retry
_RETRYABLE_STATUS_CODES = {502, 503, 504}


class DataServiceClient:
    """Client for making requests to beat-books-data service."""

    def __init__(self):
        self.base_url = settings.DATA_SERVICE_URL
        self.timeout = 30.0
        self.circuit_breaker = CircuitBreaker()
        self.max_retries = settings.RETRY_MAX_ATTEMPTS
        self.base_delay = settings.RETRY_BASE_DELAY

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make HTTP request to data service with retry logic."""
        if not self.circuit_breaker.allow_request():
            raise HTTPException(
                status_code=503,
                detail={
                    "error": {
                        "code": "CIRCUIT_OPEN",
                        "message": "Data service circuit breaker is open. Service appears to be down.",
                    }
                },
            )

        url = f"{self.base_url}{endpoint}"
        last_exception: Exception | None = None

        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.request(
                        method=method, url=url, params=params, json=json_data
                    )
                    response.raise_for_status()
                    self.circuit_breaker.record_success()
                    return response.json()

            except httpx.HTTPStatusError as e:
                if e.response.status_code in _RETRYABLE_STATUS_CODES:
                    if e.response.status_code >= 500:
                        self.circuit_breaker.record_failure()
                    last_exception = e
                    if attempt < self.max_retries - 1:
                        await self._wait_backoff(attempt)
                        continue
                # Non-retryable HTTP error — raise immediately
                if e.response.status_code >= 500:
                    self.circuit_breaker.record_failure()
                raise HTTPException(
                    status_code=e.response.status_code,
                    detail=(
                        e.response.json() if e.response.text else {"error": str(e)}
                    ),
                )
            except httpx.RequestError as e:
                self.circuit_breaker.record_failure()
                last_exception = e
                if attempt < self.max_retries - 1:
                    await self._wait_backoff(attempt)
                    continue

        # All retries exhausted
        if isinstance(last_exception, httpx.HTTPStatusError):
            raise HTTPException(
                status_code=last_exception.response.status_code,
                detail=(
                    last_exception.response.json()
                    if last_exception.response.text
                    else {"error": str(last_exception)}
                ),
            )
        raise HTTPException(
            status_code=503,
            detail={
                "error": {
                    "code": "SERVICE_UNAVAILABLE",
                    "message": f"Unable to connect to data service after {self.max_retries} attempts: {str(last_exception)}",
                }
            },
        )

    async def _wait_backoff(self, attempt: int) -> None:
        """Wait with exponential backoff and jitter."""
        delay = self.base_delay * (2**attempt)
        jitter = random.uniform(0, delay * 0.5)  # nosec B311
        await asyncio.sleep(delay + jitter)

    async def get(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make GET request."""
        return await self._make_request("GET", endpoint, params=params)

    async def post(
        self, endpoint: str, json_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make POST request."""
        return await self._make_request("POST", endpoint, json_data=json_data)


# Singleton instance
data_client = DataServiceClient()
