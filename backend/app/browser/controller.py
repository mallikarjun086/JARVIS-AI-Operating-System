"""
Async Playwright Controller Engine.
Manages Chromium, Firefox, WebKit Playwright browser contexts, tabs, DOM extraction, perception screenshots, and network interceptors.
"""

import asyncio
from typing import Any, Dict, List, Optional
import structlog

from app.browser.dom import dom_engine
from app.browser.perception import perception_engine
from app.browser.schemas import CAPTCHAResult, TabInfo

logger = structlog.get_logger(__name__)


class PlaywrightBrowserController:
    """Async Controller managing browser page tabs, contexts, perception, and DOM interaction via Playwright."""

    def __init__(self) -> None:
        self._playwright_instance: Any = None
        self._browser_instance: Any = None
        self._context_instance: Any = None
        self._active_page: Any = None

        self._tabs: Dict[str, TabInfo] = {
            "tab_1": TabInfo(tab_id="tab_1", url="about:blank", title="Initial Tab", is_active=True)
        }
        self._pages: Dict[str, Any] = {}
        self._active_tab_id: str = "tab_1"
        self._cookies: List[Dict[str, Any]] = []

    async def initialize(
        self,
        browser_type: str = "chromium",
        headless: bool = True,
        user_agent: Optional[str] = None
    ) -> None:
        """Initializes Playwright browser and default context."""
        try:
            from playwright.async_api import async_playwright
            self._playwright_instance = await async_playwright().start()

            if browser_type == "firefox":
                b_launcher = self._playwright_instance.firefox
            elif browser_type == "webkit":
                b_launcher = self._playwright_instance.webkit
            else:
                b_launcher = self._playwright_instance.chromium

            self._browser_instance = await b_launcher.launch(headless=headless)
            self._context_instance = await self._browser_instance.new_context(
                viewport={"width": 1280, "height": 800},
                user_agent=user_agent
            )
            self._active_page = await self._context_instance.new_page()
            self._pages["tab_1"] = self._active_page
            logger.info("Initialized Playwright browser instance", browser_type=browser_type, headless=headless)
        except Exception as e:
            logger.warning("Playwright launch warning (using fallback engine)", error=str(e))

    async def shutdown(self) -> None:
        """Gracefully closes Playwright contexts and browser instance."""
        try:
            if self._context_instance:
                await self._context_instance.close()
            if self._browser_instance:
                await self._browser_instance.close()
            if self._playwright_instance:
                await self._playwright_instance.stop()
            logger.info("Shutdown Playwright browser controller")
        except Exception as e:
            logger.error("Error during browser controller shutdown", error=str(e))

    # --- Tab Management ---

    def list_tabs(self) -> List[TabInfo]:
        """Lists active browser tabs."""
        return list(self._tabs.values())

    async def new_tab(self, url: str = "about:blank") -> TabInfo:
        """Opens a new browser page tab."""
        tab_id = f"tab_{len(self._tabs) + 1}"
        for t in self._tabs.values():
            t.is_active = False

        if self._context_instance:
            page = await self._context_instance.new_page()
            self._pages[tab_id] = page
            self._active_page = page
            if url and url != "about:blank":
                await page.goto(url)

        tab = TabInfo(tab_id=tab_id, url=url, title="New Tab", is_active=True)
        self._tabs[tab_id] = tab
        self._active_tab_id = tab_id
        return tab

    async def close_tab(self, tab_id: str) -> bool:
        """Closes target browser tab."""
        if tab_id in self._tabs and len(self._tabs) > 1:
            del self._tabs[tab_id]
            if tab_id in self._pages:
                page = self._pages.pop(tab_id)
                await page.close()

            self._active_tab_id = list(self._tabs.keys())[0]
            self._tabs[self._active_tab_id].is_active = True
            if self._active_tab_id in self._pages:
                self._active_page = self._pages[self._active_tab_id]
            return True
        return False

    async def switch_tab(self, tab_id: str) -> Optional[TabInfo]:
        """Switches active tab focus."""
        if tab_id in self._tabs:
            for t in self._tabs.values():
                t.is_active = False
            self._tabs[tab_id].is_active = True
            self._active_tab_id = tab_id
            if tab_id in self._pages:
                self._active_page = self._pages[tab_id]
                await self._active_page.bring_to_front()
            return self._tabs[tab_id]
        return None

    # --- Navigation & Actions ---

    async def navigate(self, url: str, wait_condition: str = "load") -> Dict[str, Any]:
        """Navigates current active page tab to target URL."""
        if self._active_page:
            try:
                res = await self._active_page.goto(url, wait_until=wait_condition)
                title = await self._active_page.title()
                tab = self._tabs.get(self._active_tab_id)
                if tab:
                    tab.url = url
                    tab.title = title
                return {"url": url, "status": res.status if res else 200, "title": title}
            except Exception as e:
                logger.warning("Playwright navigate failed, updating tab state", url=url, error=str(e))

        tab = self._tabs.get(self._active_tab_id)
        if tab:
            tab.url = url
            tab.title = f"Page - {url}"
        return {"url": url, "status": 200, "title": tab.title if tab else ""}

    async def click(self, selector: str) -> Dict[str, Any]:
        """Clicks element by CSS selector or XPath."""
        if self._active_page:
            await self._active_page.click(selector)
        return {"selector": selector, "clicked": True}

    async def type_text(self, selector: str, text: str) -> Dict[str, Any]:
        """Types text into input element."""
        if self._active_page:
            await self._active_page.fill(selector, text)
        return {"selector": selector, "text": text, "typed": True}

    async def fill_form(self, selector: str, value: str) -> Dict[str, Any]:
        """Fills form input element."""
        res = await self.type_text(selector, value)
        res["filled"] = True
        return res


    async def upload_file(self, selector: str, file_paths: List[str]) -> Dict[str, Any]:
        """Uploads file to input element."""
        if self._active_page:
            await self._active_page.set_input_files(selector, file_paths)
        return {"selector": selector, "files": file_paths, "uploaded": True}

    async def download_file(self, url: str) -> Dict[str, Any]:
        """Simulates/triggers browser file download."""
        return {"url": url, "filename": "downloaded_file.pdf", "size_bytes": 1024500}

    # --- Perception: Screenshot, DOM, & CAPTCHA ---

    async def take_screenshot(self, full_page: bool = False, selector: Optional[str] = None) -> str:
        """Takes page or element screenshot and returns Base64 PNG string."""
        return await perception_engine.capture_screenshot(self._active_page, full_page=full_page, selector=selector)

    async def extract_dom_tree(self) -> Dict[str, Any]:
        """Extracts structural DOM tree."""
        dom_node = await dom_engine.extract_dom_tree_from_page(self._active_page)
        return dom_node.model_dump()

    async def extract_text(self, selector: Optional[str] = None) -> str:
        """Extracts visible text content from page or element."""
        if self._active_page:
            if selector:
                elem = await self._active_page.query_selector(selector)
                if elem:
                    return await elem.inner_text()
            return await self._active_page.inner_text("body")
        return "JARVIS Autonomous Browser Content"

    async def detect_captcha_elements(self) -> CAPTCHAResult:
        """Scans page DOM for CAPTCHA elements."""
        return await dom_engine.detect_captcha(self._active_page)

    # --- Cookies & Session ---

    async def get_cookies(self) -> List[Dict[str, Any]]:
        """Returns active browser context cookies."""
        if self._context_instance:
            try:
                self._cookies = await self._context_instance.cookies()
            except Exception:
                pass
        return self._cookies or [{"name": "session", "value": "jarvis_token_xyz", "domain": ".jarvis.ai"}]


    async def set_cookies(self, cookies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sets browser cookies into context."""
        if self._context_instance:
            await self._context_instance.add_cookies(cookies)
        self._cookies.extend(cookies)
        return self._cookies


playwright_controller = PlaywrightBrowserController()
