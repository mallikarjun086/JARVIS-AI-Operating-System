"""
Sliding-Window Rate Limiting Engine.
Prevents DoS and brute-force attacks by limiting request rates per IP / User.
"""

from datetime import datetime, timedelta
from typing import Dict, List
from app.security.schemas import RateLimitConfig


class RateLimiterEngine:
    """Sliding-window rate limiter tracking requests per IP."""

    def __init__(self, max_requests_per_minute: int = 100) -> None:
        self.max_requests = max_requests_per_minute
        self._history: Dict[str, List[datetime]] = {}

    def check_rate_limit(self, ip_address: str = "127.0.0.1") -> RateLimitConfig:
        """
        Enforces sliding window limit. Returns RateLimitConfig telemetry.
        """
        now = datetime.utcnow()
        cutoff = now - timedelta(minutes=1)

        if ip_address not in self._history:
            self._history[ip_address] = []

        # Filter timestamps older than 1 minute
        self._history[ip_address] = [t for t in self._history[ip_address] if t > cutoff]
        self._history[ip_address].append(now)

        current_count = len(self._history[ip_address])
        is_limited = current_count > self.max_requests

        return RateLimitConfig(
            ip_address=ip_address,
            requests_per_minute=self.max_requests,
            current_count=current_count,
            is_rate_limited=is_limited
        )


rate_limiter = RateLimiterEngine()
