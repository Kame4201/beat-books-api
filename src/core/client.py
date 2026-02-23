"""HTTP client for communicating with beat-books-data service."""

import httpx
from typing import Optional, Dict, Any
from fastapi import HTTPException
from src.core.config import settings
from src.core.circuit_breaker import CircuitBreaker


class DataServiceClient:
    """Client for making requests to beat-books-data service."""

    def __init__(self):
        self.base_url = settings.DATA_SERVICE_URL
        self.timeout = 30.0
        self.circuit_breaker = CircuitBreaker()

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make HTTP request to data service."""
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

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.request(
                    method=method, url=url, params=params, json=json_data
                )
                response.raise_for_status()
                self.circuit_breaker.record_success()
                return response.json()

        except httpx.HTTPStatusError as e:
            # Don't trip circuit breaker on client errors (4xx)
            if e.response.status_code >= 500:
                self.circuit_breaker.record_failure()
            raise HTTPException(
                status_code=e.response.status_code,
                detail=e.response.json() if e.response.text else {"error": str(e)},
            )
        except httpx.RequestError as e:
            self.circuit_breaker.record_failure()
            raise HTTPException(
                status_code=503,
                detail={
                    "error": {
                        "code": "SERVICE_UNAVAILABLE",
                        "message": f"Unable to connect to data service: {str(e)}",
                    }
                },
            )

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
