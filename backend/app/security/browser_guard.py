"""
Secure Browser Session Context Isolation Manager.
Enforces incognito isolation, SameSite cookies, anti-CSRF headers, and HTTPS security for browser automation sessions.
"""

from typing import Any, Dict


class SecureBrowserSessionGuard:
    """Configures secure isolated Playwright browser contexts."""

    @classmethod
    def get_secure_context_options(cls) -> Dict[str, Any]:
        """
        Returns security context configuration for Playwright browser.
        Enforces incognito mode, HTTPS, SameSite Strict cookies, anti-CSRF headers.
        """
        return {
            "is_incognito": True,
            "enforce_https": True,
            "cookie_samesite": "Strict",
            "csrf_protection": True,
            "user_data_dir": None,  # Isolated in-memory profile
            "extra_http_headers": {
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "DENY",
                "X-XSS-Protection": "1; mode=block",
                "Strict-Transport-Security": "max-age=31536000; includeSubDomains"
            }
        }


browser_session_guard = SecureBrowserSessionGuard()
