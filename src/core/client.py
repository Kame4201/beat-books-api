"""HTTP client for communicating with beat-books-data service."""
import httpx
from typing import Optional, Dict, Any
from fastapi import HTTPException
from src.core.config import settings


class DataServiceClient:
    """Client for making requests to beat-books-data service."""

    def __init__(self):
        self.base_url = settings.DATA_SERVICE_URL
        self.timeout = 30.0

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make HTTP request to data service."""
        url = f"{self.base_url}{endpoint}"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.request(
                    method=method, url=url, params=params, json=json_data
                )
                response.raise_for_status()
                return response.json()

        except httpx.HTTPStatusError as e:
            # Forward the error from the data service
            raise HTTPException(
                status_code=e.response.status_code,
                detail=e.response.json() if e.response.text else {"error": str(e)},
            )
        except httpx.RequestError as e:
            # Connection errors, timeouts, etc.
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
