"""Tests for retry logic with exponential backoff (issue #25)."""

from unittest.mock import AsyncMock, patch, MagicMock

import httpx
import pytest

from src.core.client import DataServiceClient


@pytest.fixture
def retry_client():
    client = DataServiceClient()
    client.max_retries = 3
    client.base_delay = 0.01  # Fast tests
    return client


class TestRetryOnTransientErrors:
    """Verify retries happen on transient errors."""

    @pytest.mark.asyncio
    async def test_retries_on_connection_error(self, retry_client):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "ok"}
        mock_response.raise_for_status = MagicMock()

        call_count = 0

        async def mock_request(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise httpx.ConnectError("Connection refused")
            return mock_response

        with patch("src.core.client.httpx.AsyncClient") as mock_cls:
            mock_http = AsyncMock()
            mock_http.request = mock_request
            mock_http.__aenter__ = AsyncMock(return_value=mock_http)
            mock_http.__aexit__ = AsyncMock(return_value=False)
            mock_cls.return_value = mock_http

            result = await retry_client._make_request("GET", "/test")
            assert result == {"data": "ok"}
            assert call_count == 3

    @pytest.mark.asyncio
    async def test_retries_on_502(self, retry_client):
        call_count = 0

        mock_success = MagicMock()
        mock_success.status_code = 200
        mock_success.json.return_value = {"data": "ok"}
        mock_success.raise_for_status = MagicMock()

        mock_502 = MagicMock()
        mock_502.status_code = 502
        mock_502.text = '{"error": "bad gateway"}'
        mock_502.json.return_value = {"error": "bad gateway"}

        async def mock_request(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                resp = mock_502
                raise httpx.HTTPStatusError("502", request=MagicMock(), response=resp)
            return mock_success

        with patch("src.core.client.httpx.AsyncClient") as mock_cls:
            mock_http = AsyncMock()
            mock_http.request = mock_request
            mock_http.__aenter__ = AsyncMock(return_value=mock_http)
            mock_http.__aexit__ = AsyncMock(return_value=False)
            mock_cls.return_value = mock_http

            result = await retry_client._make_request("GET", "/test")
            assert result == {"data": "ok"}
            assert call_count == 2

    @pytest.mark.asyncio
    async def test_retries_on_503(self, retry_client):
        call_count = 0

        mock_success = MagicMock()
        mock_success.status_code = 200
        mock_success.json.return_value = {"ok": True}
        mock_success.raise_for_status = MagicMock()

        mock_503 = MagicMock()
        mock_503.status_code = 503
        mock_503.text = "{}"
        mock_503.json.return_value = {}

        async def mock_request(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise httpx.HTTPStatusError(
                    "503", request=MagicMock(), response=mock_503
                )
            return mock_success

        with patch("src.core.client.httpx.AsyncClient") as mock_cls:
            mock_http = AsyncMock()
            mock_http.request = mock_request
            mock_http.__aenter__ = AsyncMock(return_value=mock_http)
            mock_http.__aexit__ = AsyncMock(return_value=False)
            mock_cls.return_value = mock_http

            result = await retry_client._make_request("GET", "/test")
            assert result == {"ok": True}
            assert call_count == 3


class TestNoRetryOnClientErrors:
    """Verify client errors are NOT retried."""

    @pytest.mark.asyncio
    async def test_no_retry_on_400(self, retry_client):
        call_count = 0

        mock_400 = MagicMock()
        mock_400.status_code = 400
        mock_400.text = '{"error": "bad request"}'
        mock_400.json.return_value = {"error": "bad request"}

        async def mock_request(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            raise httpx.HTTPStatusError("400", request=MagicMock(), response=mock_400)

        with patch("src.core.client.httpx.AsyncClient") as mock_cls:
            mock_http = AsyncMock()
            mock_http.request = mock_request
            mock_http.__aenter__ = AsyncMock(return_value=mock_http)
            mock_http.__aexit__ = AsyncMock(return_value=False)
            mock_cls.return_value = mock_http

            with pytest.raises(Exception):
                await retry_client._make_request("GET", "/test")
            assert call_count == 1

    @pytest.mark.asyncio
    async def test_no_retry_on_404(self, retry_client):
        call_count = 0

        mock_404 = MagicMock()
        mock_404.status_code = 404
        mock_404.text = '{"error": "not found"}'
        mock_404.json.return_value = {"error": "not found"}

        async def mock_request(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            raise httpx.HTTPStatusError("404", request=MagicMock(), response=mock_404)

        with patch("src.core.client.httpx.AsyncClient") as mock_cls:
            mock_http = AsyncMock()
            mock_http.request = mock_request
            mock_http.__aenter__ = AsyncMock(return_value=mock_http)
            mock_http.__aexit__ = AsyncMock(return_value=False)
            mock_cls.return_value = mock_http

            with pytest.raises(Exception):
                await retry_client._make_request("GET", "/test")
            assert call_count == 1


class TestRetryExhaustion:
    """Verify behavior when all retries are exhausted."""

    @pytest.mark.asyncio
    async def test_raises_503_after_all_retries_exhausted(self, retry_client):
        async def mock_request(*args, **kwargs):
            raise httpx.ConnectError("Connection refused")

        with patch("src.core.client.httpx.AsyncClient") as mock_cls:
            mock_http = AsyncMock()
            mock_http.request = mock_request
            mock_http.__aenter__ = AsyncMock(return_value=mock_http)
            mock_http.__aexit__ = AsyncMock(return_value=False)
            mock_cls.return_value = mock_http

            with pytest.raises(Exception) as exc_info:
                await retry_client._make_request("GET", "/test")
            assert exc_info.value.status_code == 503
            assert "3 attempts" in exc_info.value.detail["error"]["message"]


class TestBackoff:
    """Verify exponential backoff timing."""

    @pytest.mark.asyncio
    async def test_backoff_increases_exponentially(self, retry_client):
        delays = []

        async def mock_sleep(duration):
            delays.append(duration)

        async def mock_request(*args, **kwargs):
            raise httpx.ConnectError("Connection refused")

        with patch("src.core.client.httpx.AsyncClient") as mock_cls, patch(
            "src.core.client.asyncio.sleep", side_effect=mock_sleep
        ):
            mock_http = AsyncMock()
            mock_http.request = mock_request
            mock_http.__aenter__ = AsyncMock(return_value=mock_http)
            mock_http.__aexit__ = AsyncMock(return_value=False)
            mock_cls.return_value = mock_http

            with pytest.raises(Exception):
                await retry_client._make_request("GET", "/test")

        # Should have 2 delays (between 3 attempts)
        assert len(delays) == 2
        # Second delay should be larger than first (exponential)
        assert delays[1] > delays[0]
