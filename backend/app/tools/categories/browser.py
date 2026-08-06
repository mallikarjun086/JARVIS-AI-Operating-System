"""
Browser Automation Tools Package for Enterprise Tool Framework.
Registers 13 production tools for Playwright browser automation.
"""

from typing import Any, Dict, List, Optional
from app.browser.manager import browser_manager
from app.browser.schemas import BrowserActionRequest, BrowserActionType
from app.tools.base import BaseTool
from app.tools.schemas import PermissionLevel


class BrowserOpenTool(BaseTool):
    """Tool to open a new browser session context."""

    def __init__(self) -> None:
        super().__init__(
            name="browser.open",
            description="Opens a new browser tab or session context",
            category="browser",
            version="1.0.0"
        )

    @property
    def permission_level(self) -> PermissionLevel:

        return PermissionLevel.NETWORK

    async def execute(self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = parameters.get("url", "about:blank")
        req = BrowserActionRequest(action_type=BrowserActionType.OPEN, url=url)
        res = await browser_manager.execute_action(req)
        return {"status": res.status, "result": res.result}


class BrowserNavigateTool(BaseTool):
    """Tool to navigate to a target URL."""

    def __init__(self) -> None:
        super().__init__(
            name="browser.navigate",
            description="Navigates the browser page tab to a target URL",
            category="browser",
            version="1.0.0"
        )

    @property
    def permission_level(self) -> PermissionLevel:

        return PermissionLevel.NETWORK

    async def execute(self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = parameters.get("url", "https://example.com")
        req = BrowserActionRequest(action_type=BrowserActionType.NAVIGATE, url=url)
        res = await browser_manager.execute_action(req)
        return {"status": res.status, "result": res.result}


class BrowserClickTool(BaseTool):
    """Tool to click a page element by CSS selector or XPath."""

    def __init__(self) -> None:
        super().__init__(
            name="browser.click",
            description="Clicks an interactive DOM element by CSS selector or XPath",
            category="browser",
            version="1.0.0"
        )

    @property
    def permission_level(self) -> PermissionLevel:

        return PermissionLevel.NETWORK

    async def execute(self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        selector = parameters.get("selector", "button")
        req = BrowserActionRequest(action_type=BrowserActionType.CLICK, selector=selector)
        res = await browser_manager.execute_action(req)
        return {"status": res.status, "result": res.result}


class BrowserTypeTool(BaseTool):
    """Tool to type text into input elements."""

    def __init__(self) -> None:
        super().__init__(
            name="browser.type",
            description="Types text into an input or textarea element",
            category="browser",
            version="1.0.0"
        )

    @property
    def permission_level(self) -> PermissionLevel:

        return PermissionLevel.NETWORK

    async def execute(self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        selector = parameters.get("selector", "input")
        value = parameters.get("value", "")
        req = BrowserActionRequest(action_type=BrowserActionType.TYPE, selector=selector, value=value)
        res = await browser_manager.execute_action(req)
        return {"status": res.status, "result": res.result}


class BrowserWaitTool(BaseTool):
    """Tool to pause or wait for page conditions."""

    def __init__(self) -> None:
        super().__init__(
            name="browser.wait",
            description="Waits for a selector or timeout duration in seconds",
            category="browser",
            version="1.0.0"
        )

    @property
    def permission_level(self) -> PermissionLevel:

        return PermissionLevel.READ_ONLY

    async def execute(self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        seconds = float(parameters.get("seconds", 1.0))
        req = BrowserActionRequest(action_type=BrowserActionType.WAIT, wait_time_seconds=seconds)
        res = await browser_manager.execute_action(req)
        return {"status": res.status, "result": res.result}


class BrowserExtractTextTool(BaseTool):
    """Tool to extract visible text content from page."""

    def __init__(self) -> None:
        super().__init__(
            name="browser.extract_text",
            description="Extracts visible text content from the active page or element",
            category="browser",
            version="1.0.0"
        )

    @property
    def permission_level(self) -> PermissionLevel:

        return PermissionLevel.READ_ONLY

    async def execute(self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        selector = parameters.get("selector")
        req = BrowserActionRequest(action_type=BrowserActionType.EXTRACT_TEXT, selector=selector)
        res = await browser_manager.execute_action(req)
        return {"status": res.status, "result": res.result}


class BrowserExtractHTMLTool(BaseTool):
    """Tool to extract raw DOM or HTML content."""

    def __init__(self) -> None:
        super().__init__(
            name="browser.extract_html",
            description="Extracts raw structural HTML DOM tree or element source",
            category="browser",
            version="1.0.0"
        )

    @property
    def permission_level(self) -> PermissionLevel:

        return PermissionLevel.READ_ONLY

    async def execute(self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        req = BrowserActionRequest(action_type=BrowserActionType.EXTRACT_DOM)
        res = await browser_manager.execute_action(req)
        return {"status": res.status, "result": res.result}


class BrowserScreenshotTool(BaseTool):
    """Tool to capture browser viewport or full page screenshot."""

    def __init__(self) -> None:
        super().__init__(
            name="browser.screenshot",
            description="Captures page screenshot as Base64 encoded PNG string",
            category="browser",
            version="1.0.0"
        )

    @property
    def permission_level(self) -> PermissionLevel:

        return PermissionLevel.READ_ONLY

    async def execute(self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        selector = parameters.get("selector")
        req = BrowserActionRequest(action_type=BrowserActionType.SCREENSHOT, selector=selector)
        res = await browser_manager.execute_action(req)
        res_dict = res.result if isinstance(res.result, dict) else {"image_base64": str(res.result or "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==")}
        return {"status": res.status, "result": res_dict, "image_base64": res_dict.get("image_base64", "")}



class BrowserDownloadTool(BaseTool):
    """Tool to trigger and download a file."""

    def __init__(self) -> None:
        super().__init__(
            name="browser.download",
            description="Downloads a file from target URL into workspace",
            category="browser",
            version="1.0.0"
        )

    @property
    def permission_level(self) -> PermissionLevel:

        return PermissionLevel.NETWORK

    async def execute(self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = parameters.get("url", "https://example.com/file.pdf")
        req = BrowserActionRequest(action_type=BrowserActionType.DOWNLOAD_FILE, url=url)
        res = await browser_manager.execute_action(req)
        return {"status": res.status, "result": res.result}


class BrowserUploadTool(BaseTool):
    """Tool to upload files to an input element."""

    def __init__(self) -> None:
        super().__init__(
            name="browser.upload",
            description="Uploads one or more files to a file input element",
            category="browser",
            version="1.0.0"
        )

    @property
    def permission_level(self) -> PermissionLevel:

        return PermissionLevel.WRITE

    async def execute(self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        selector = parameters.get("selector", "#file-input")
        files = parameters.get("files", [])
        req = BrowserActionRequest(action_type=BrowserActionType.UPLOAD_FILE, selector=selector, files=files)
        res = await browser_manager.execute_action(req)
        return {"status": res.status, "result": res.result}


class BrowserCloseTool(BaseTool):
    """Tool to close browser tab or context."""

    def __init__(self) -> None:
        super().__init__(
            name="browser.close",
            description="Closes active browser tab or context",
            category="browser",
            version="1.0.0"
        )

    @property
    def permission_level(self) -> PermissionLevel:

        return PermissionLevel.READ_ONLY

    async def execute(self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        tab_id = parameters.get("tab_id", "tab_1")
        req = BrowserActionRequest(action_type=BrowserActionType.CLOSE_TAB, tab_id=tab_id)
        res = await browser_manager.execute_action(req)
        return {"status": res.status, "result": res.result}


class BrowserCookiesTool(BaseTool):
    """Tool to inspect or inject browser cookies."""

    def __init__(self) -> None:
        super().__init__(
            name="browser.cookies",
            description="Gets or sets active browser context cookies",
            category="browser",
            version="1.0.0"
        )

    @property
    def permission_level(self) -> PermissionLevel:

        return PermissionLevel.NETWORK

    async def execute(self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        cookies = parameters.get("cookies")
        if cookies:
            req = BrowserActionRequest(action_type=BrowserActionType.SET_COOKIES, cookies=cookies)
        else:
            req = BrowserActionRequest(action_type=BrowserActionType.GET_COOKIES)
        res = await browser_manager.execute_action(req)
        return {"status": res.status, "result": res.result}


class BrowserTabsTool(BaseTool):
    """Tool to manage or switch browser tabs."""

    def __init__(self) -> None:
        super().__init__(
            name="browser.tabs",
            description="Lists open tabs or switches active browser tab focus",
            category="browser",
            version="1.0.0"
        )

    @property
    def permission_level(self) -> PermissionLevel:

        return PermissionLevel.READ_ONLY

    async def execute(self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        tab_id = parameters.get("tab_id")
        if tab_id:
            req = BrowserActionRequest(action_type=BrowserActionType.SWITCH_TAB, tab_id=tab_id)
            res = await browser_manager.execute_action(req)
            return {"status": res.status, "result": res.result}
        else:
            from app.browser.controller import playwright_controller
            return {"tabs": [t.model_dump() for t in playwright_controller.list_tabs()]}
