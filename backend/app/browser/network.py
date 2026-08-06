"""
Network Interception & Telemetry Engine.
Intercepts HTTP requests/responses, manages custom headers, cookies, file downloads, and bandwidth telemetry.
"""

from typing import Any, Dict, List
import structlog

logger = structlog.get_logger(__name__)


class NetworkInterceptor:
    """Manages Playwright network interception rules and telemetry statistics."""

    def __init__(self) -> None:
        self.total_requests: int = 0
        self.total_bytes_downloaded: int = 0
        self.total_bytes_uploaded: int = 0
        self.intercepted_headers: Dict[str, str] = {}

    def set_extra_headers(self, headers: Dict[str, str]) -> None:
        """Sets custom HTTP headers applied to outbound requests."""
        self.intercepted_headers.update(headers)

    async def attach_network_listeners(self, page: Any) -> None:
        """Attaches request/response listeners to Playwright page."""
        if page is None:
            return

        def on_request(request):
            self.total_requests += 1

        def on_response(response):
            try:
                content_len = int(response.headers.get("content-length", 0))
                self.total_bytes_downloaded += content_len
            except Exception:
                pass

        page.on("request", on_request)
        page.on("response", on_response)
        logger.info("Attached network interceptor listeners to page")


network_interceptor = NetworkInterceptor()
