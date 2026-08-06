"""
Browser Automation Manager Engine.
Orchestrates Playwright browser lifecycle, context pooling, error recovery, safety gatekeeper, and telemetry.
"""

import time
from typing import Any, Dict, Optional
import structlog

from app.browser.agent import ai_navigator
from app.browser.controller import playwright_controller
from app.browser.human_approval import human_approval_gatekeeper
from app.browser.metrics import browser_metrics
from app.browser.recovery import browser_recovery
from app.browser.schemas import (
    ApprovalStatus,
    BrowserActionRequest,
    BrowserActionResponse,
    BrowserActionType,
    BrowserConfig,
    HighRiskActionType,
)
from app.browser.session import session_manager

logger = structlog.get_logger(__name__)


class BrowserAutomationManager:
    """Central manager orchestrating Playwright automation, lifecycle, safety gatekeeper, and AI navigation."""

    def __init__(self) -> None:
        self._is_initialized: bool = False
        self._config: BrowserConfig = BrowserConfig()

    async def initialize(self, config: Optional[BrowserConfig] = None) -> None:
        """Initializes browser controller and loads optional persistent session profile."""
        if config:
            self._config = config

        await playwright_controller.initialize(
            browser_type=self._config.browser_type.value,
            headless=self._config.headless,
            user_agent=self._config.user_agent
        )

        if self._config.session_profile_name:
            profile = session_manager.load_session(self._config.session_profile_name)
            if profile and profile.cookies:
                await playwright_controller.set_cookies(profile.cookies)

        self._is_initialized = True
        logger.info("BrowserAutomationManager initialized successfully")

    async def shutdown(self) -> None:
        """Gracefully shuts down browser manager."""
        await playwright_controller.shutdown()
        self._is_initialized = False
        logger.info("BrowserAutomationManager shutdown completed")

    async def get_health_status(self) -> Dict[str, Any]:
        """Returns browser manager health diagnostics."""
        return {
            "initialized": self._is_initialized,
            "browser_type": self._config.browser_type.value,
            "headless": self._config.headless,
            "active_tabs": len(playwright_controller.list_tabs()),
            "saved_profiles": session_manager.list_profiles()
        }

    async def execute_action(self, req: BrowserActionRequest) -> BrowserActionResponse:
        """
        Executes browser action with error recovery and safety gatekeeper interception.
        """
        if not self._is_initialized:
            await self.initialize()

        # 1. Human Approval Gatekeeper Interception for High-Risk Actions
        if req.high_risk_type is not None:
            browser_metrics.total_approvals_requested += 1
            ticket = human_approval_gatekeeper.create_approval_request(
                high_risk_type=req.high_risk_type,
                target_details={"action_type": req.action_type.value, "url": req.url, "value": req.value}
            )
            return BrowserActionResponse(
                action_type=req.action_type,
                status="PENDING_HUMAN_APPROVAL",
                requires_approval=True,
                approval_id=ticket.approval_id,
                error_message=f"High-risk action '{req.high_risk_type.value}' requires human approval before proceeding."
            )

        resp = BrowserActionResponse(action_type=req.action_type, status="SUCCESS")
        start_time = time.time()

        try:
            # 2. Action Execution Dispatcher
            if req.action_type == BrowserActionType.OPEN:
                resp.result = await playwright_controller.new_tab(req.url or "about:blank")

            elif req.action_type == BrowserActionType.NAVIGATE:
                url = req.url or "https://example.com"
                resp.result = await playwright_controller.navigate(url)
                browser_metrics.record_navigation((time.time() - start_time) * 1000.0)

            elif req.action_type == BrowserActionType.CLICK:
                resp.result = await playwright_controller.click(req.selector or "button")
                browser_metrics.record_interaction((time.time() - start_time) * 1000.0)

            elif req.action_type == BrowserActionType.TYPE or req.action_type == BrowserActionType.FILL_FORM:
                resp.result = await playwright_controller.fill_form(req.selector or "input", req.value or "")
                browser_metrics.record_interaction((time.time() - start_time) * 1000.0)

            elif req.action_type == BrowserActionType.WAIT:
                import asyncio
                await asyncio.sleep(req.wait_time_seconds or 1.0)
                resp.result = {"waited_seconds": req.wait_time_seconds or 1.0}

            elif req.action_type == BrowserActionType.UPLOAD_FILE:
                resp.result = await playwright_controller.upload_file(req.selector or "#file-upload", req.files)
                browser_metrics.total_uploads += len(req.files)

            elif req.action_type == BrowserActionType.DOWNLOAD_FILE:
                resp.result = await playwright_controller.download_file(req.url or "https://example.com/file.pdf")
                browser_metrics.total_downloads += 1

            elif req.action_type == BrowserActionType.NEW_TAB:
                tab = await playwright_controller.new_tab(req.url or "about:blank")
                resp.result = tab.model_dump()

            elif req.action_type == BrowserActionType.CLOSE_TAB:
                tab_id = req.tab_id or "tab_1"
                closed = await playwright_controller.close_tab(tab_id)
                resp.result = {"closed": closed}

            elif req.action_type == BrowserActionType.SWITCH_TAB:
                tab_id = req.tab_id or "tab_1"
                switched = await playwright_controller.switch_tab(tab_id)
                resp.result = switched.model_dump() if switched else {}

            elif req.action_type == BrowserActionType.GET_COOKIES:
                resp.result = await playwright_controller.get_cookies()

            elif req.action_type == BrowserActionType.SET_COOKIES:
                resp.result = await playwright_controller.set_cookies(req.cookies)

            elif req.action_type == BrowserActionType.SAVE_SESSION:
                cookies = await playwright_controller.get_cookies()
                prof_name = req.value or "default_profile"
                saved_prof = session_manager.save_session(prof_name, cookies)
                resp.result = saved_prof.model_dump()

            elif req.action_type == BrowserActionType.RESTORE_SESSION:
                prof_name = req.value or "default_profile"
                loaded_prof = session_manager.load_session(prof_name)
                if loaded_prof:
                    await playwright_controller.set_cookies(loaded_prof.cookies)
                    resp.result = {"restored": True, "profile": prof_name}
                else:
                    resp.result = {"restored": False, "message": f"Profile '{prof_name}' not found."}

            elif req.action_type == BrowserActionType.SCREENSHOT:
                b64 = await playwright_controller.take_screenshot(selector=req.selector)
                resp.result = {"image_base64": b64}
                browser_metrics.total_screenshots += 1

            elif req.action_type == BrowserActionType.EXTRACT_TEXT:
                text = await playwright_controller.extract_text(selector=req.selector)
                resp.result = {"text": text}

            elif req.action_type == BrowserActionType.EXTRACT_DOM:
                dom_data = await playwright_controller.extract_dom_tree()
                resp.result = dom_data
                browser_metrics.record_dom_extraction((time.time() - start_time) * 1000.0)

            elif req.action_type == BrowserActionType.DETECT_CAPTCHA:
                captcha = await playwright_controller.detect_captcha_elements()
                resp.result = captcha.model_dump()

            elif req.action_type == BrowserActionType.AI_NAVIGATE:
                nav_result = await ai_navigator.navigate_with_ai(req.ai_prompt or "Navigate and fill form")
                resp.result = nav_result

        except Exception as e:
            logger.error("Browser action execution error", action_type=req.action_type.value, error=str(e))
            resp.status = "FAILED"
            resp.error_message = str(e)
            browser_metrics.total_crashes += 1

        return resp


browser_manager = BrowserAutomationManager()
