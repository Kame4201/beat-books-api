"""Tests for circuit breaker pattern (issue #24)."""

import time

from src.core.circuit_breaker import CircuitBreaker, CircuitState


class TestCircuitBreakerClosed:
    """Tests for CLOSED state (normal operation)."""

    def test_initial_state_is_closed(self):
        cb = CircuitBreaker(failure_threshold=3, reset_timeout=10.0)
        assert cb.state == CircuitState.CLOSED

    def test_allows_request_when_closed(self):
        cb = CircuitBreaker(failure_threshold=3, reset_timeout=10.0)
        assert cb.allow_request() is True

    def test_stays_closed_below_threshold(self):
        cb = CircuitBreaker(failure_threshold=3, reset_timeout=10.0)
        cb.record_failure()
        cb.record_failure()
        assert cb.state == CircuitState.CLOSED
        assert cb.allow_request() is True

    def test_success_resets_failure_count(self):
        cb = CircuitBreaker(failure_threshold=3, reset_timeout=10.0)
        cb.record_failure()
        cb.record_failure()
        cb.record_success()
        cb.record_failure()
        cb.record_failure()
        assert cb.state == CircuitState.CLOSED


class TestCircuitBreakerOpen:
    """Tests for OPEN state (fast-fail)."""

    def test_opens_at_threshold(self):
        cb = CircuitBreaker(failure_threshold=3, reset_timeout=10.0)
        cb.record_failure()
        cb.record_failure()
        cb.record_failure()
        assert cb.state == CircuitState.OPEN

    def test_denies_request_when_open(self):
        cb = CircuitBreaker(failure_threshold=3, reset_timeout=10.0)
        for _ in range(3):
            cb.record_failure()
        assert cb.allow_request() is False


class TestCircuitBreakerHalfOpen:
    """Tests for HALF-OPEN state (recovery testing)."""

    def test_transitions_to_half_open_after_timeout(self):
        cb = CircuitBreaker(failure_threshold=3, reset_timeout=0.1)
        for _ in range(3):
            cb.record_failure()
        assert cb.state == CircuitState.OPEN

        time.sleep(0.15)
        assert cb.state == CircuitState.HALF_OPEN

    def test_allows_request_when_half_open(self):
        cb = CircuitBreaker(failure_threshold=3, reset_timeout=0.1)
        for _ in range(3):
            cb.record_failure()
        time.sleep(0.15)
        assert cb.allow_request() is True

    def test_success_in_half_open_closes_circuit(self):
        cb = CircuitBreaker(failure_threshold=3, reset_timeout=0.1)
        for _ in range(3):
            cb.record_failure()
        time.sleep(0.15)
        assert cb.state == CircuitState.HALF_OPEN

        cb.record_success()
        assert cb.state == CircuitState.CLOSED

    def test_failure_in_half_open_reopens_circuit(self):
        cb = CircuitBreaker(failure_threshold=1, reset_timeout=0.1)
        cb.record_failure()
        assert cb.state == CircuitState.OPEN

        time.sleep(0.15)
        assert cb.state == CircuitState.HALF_OPEN

        cb.record_failure()
        assert cb.state == CircuitState.OPEN


class TestCircuitBreakerIntegration:
    """Integration tests with DataServiceClient."""

    def test_circuit_open_returns_503(self, client):
        from src.core.client import data_client

        # Trip the circuit breaker
        original_threshold = data_client.circuit_breaker.failure_threshold
        data_client.circuit_breaker.failure_threshold = 1
        data_client.circuit_breaker.record_failure()

        try:
            response = client.get("/scrape/2024")
            assert response.status_code == 503
            assert "CIRCUIT_OPEN" in response.json()["detail"]["error"]["code"]
        finally:
            # Reset state
            data_client.circuit_breaker.record_success()
            data_client.circuit_breaker.failure_threshold = original_threshold
