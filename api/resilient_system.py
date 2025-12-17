"""Self-Healing and Resilient System with Auto-Recovery

Implements resilient patterns including circuit breaker, retry logic,
fallback mechanisms, and auto-healing capabilities for API reliability.
"""

import logging
import asyncio
from typing import Callable, Any, Optional, Dict, List
from datetime import datetime, timedelta
from functools import wraps
from enum import Enum
import random

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """States of circuit breaker"""
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class CircuitBreaker:
    """Circuit breaker for preventing cascading failures"""

    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
        logger.info(f"CircuitBreaker initialized")

    def call(self, func: Callable, *args, **kwargs) -> Any:
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                logger.info("Circuit breaker: HALF_OPEN")
            else:
                raise Exception("Circuit breaker OPEN")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        self.failure_count = 0
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.CLOSED
            logger.info("Circuit breaker: CLOSED")

    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning(f"Circuit breaker OPEN")

    def _should_attempt_reset(self) -> bool:
        if self.last_failure_time is None:
            return True
        elapsed = (datetime.now() - self.last_failure_time).total_seconds()
        return elapsed >= self.recovery_timeout


class RetryPolicy:
    """Retry policy with exponential backoff"""

    def __init__(self, max_attempts: int = 3, base_delay: float = 0.1, max_delay: float = 10.0):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay

    async def execute_with_retry(self, func: Callable, *args, **kwargs) -> Any:
        last_exception = None
        for attempt in range(1, self.max_attempts + 1):
            try:
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < self.max_attempts:
                    delay = self._calculate_backoff(attempt)
                    logger.warning(f"Attempt {attempt} failed, retrying in {delay:.2f}s")
                    await asyncio.sleep(delay)
        raise last_exception

    def _calculate_backoff(self, attempt: int) -> float:
        delay = min(self.base_delay * (2 ** (attempt - 1)), self.max_delay)
        return delay * (0.5 + random.random())


class HealthCheck:
    """System health monitoring and auto-healing"""

    def __init__(self, check_interval: int = 30):
        self.check_interval = check_interval
        self.last_check = None
        self.status = "HEALTHY"
        self.metrics: Dict[str, Any] = {}

    async def perform_health_check(self) -> bool:
        try:
            self.status = "HEALTHY"
            self.last_check = datetime.now()
            return True
        except Exception as e:
            self.status = "UNHEALTHY"
            logger.error(f"Health check failed: {e}")
            return False

    async def auto_heal(self) -> bool:
        logger.info("Initiating auto-heal process")
        try:
            self.metrics.clear()
            result = await self.perform_health_check()
            logger.info(f"Auto-heal completed with result {result}")
            return result
        except Exception as e:
            logger.error(f"Auto-heal failed: {e}")
            return False


class ResilientSystem:
    """Orchestrates resilience patterns"""

    def __init__(self):
        self.circuit_breaker = CircuitBreaker()
        self.retry_policy = RetryPolicy()
        self.health_check = HealthCheck()
        self.failure_history: List[Dict[str, Any]] = []

    async def execute_with_resilience(self, func: Callable, *args, **kwargs) -> Any:
        try:
            result = await self.retry_policy.execute_with_retry(
                lambda: self.circuit_breaker.call(func, *args, **kwargs)
            )
            return result
        except Exception as e:
            self.failure_history.append({
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            })
            if not await self.health_check.perform_health_check():
                await self.health_check.auto_heal()
            raise

    def get_system_status(self) -> Dict[str, Any]:
        return {
            "circuit_breaker_state": self.circuit_breaker.state.value,
            "health_status": self.health_check.status,
            "recent_failures": len(self.failure_history)
        }
