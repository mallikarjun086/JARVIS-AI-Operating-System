"""
Desktop Automation Tools Package for Enterprise Tool Framework (Sprint 7 & 7.1).
Registers 20 production desktop tools with capability metadata.
"""

from typing import Any, Dict, Optional
from app.desktop.manager import desktop_manager
from app.desktop.schemas import DesktopActionRequest, DesktopActionType, DesktopToolMetadata
from app.tools.base import BaseTool
from app.tools.schemas import PermissionLevel


class BaseDesktopTool(BaseTool):
    """Base class for all Desktop tools exposing capability metadata."""

    def __init__(self, name: str, description: str, perm_level: PermissionLevel = PermissionLevel.SYSTEM) -> None:
        super().__init__(name=name, description=description, category="desktop", version="1.0.0")
        self._perm_level = perm_level

    @property
    def permission_level(self) -> PermissionLevel:
        return self._perm_level

    def get_capability_metadata(self) -> DesktopToolMetadata:
        return DesktopToolMetadata(
            tool_name=self.name,
            version=self.version,
            description=self.description,
            permission_level=self.permission_level
        )



class DesktopLaunchAppTool(BaseDesktopTool):
    def __init__(self) -> None:
        super().__init__("desktop.launch_app", "Launches a desktop application executable or system alias", PermissionLevel.SYSTEM)

    async def execute(self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        app = parameters.get("app_name_or_path", "notepad")
        req = DesktopActionRequest(action_type=DesktopActionType.LAUNCH_APP, app_name_or_path=app)
        res = await desktop_manager.execute_action(req)
        return {"status": res.status.value, "result": res.result}


class DesktopCloseAppTool(BaseDesktopTool):
    def __init__(self) -> None:
        super().__init__("desktop.close_app", "Terminates a running desktop application process", PermissionLevel.SYSTEM)

    async def execute(self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        app = parameters.get("app_name_or_path", "")
        req = DesktopActionRequest(action_type=DesktopActionType.CLOSE_APP, app_name_or_path=app)
        res = await desktop_manager.execute_action(req)
        return {"status": res.status.value, "result": res.result}


class DesktopFindWindowTool(BaseDesktopTool):
    def __init__(self) -> None:
        super().__init__("desktop.find_window", "Finds desktop window handle by title substring or HWND", PermissionLevel.READ_ONLY)

    async def execute(self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        title = parameters.get("title_or_hwnd")
        req = DesktopActionRequest(action_type=DesktopActionType.FIND_WINDOW, window_title_or_hwnd=title)
        res = await desktop_manager.execute_action(req)
        return {"status": res.status.value, "result": res.result}


class DesktopFocusWindowTool(BaseDesktopTool):
    def __init__(self) -> None:
        super().__init__("desktop.focus_window", "Brings target desktop window into active foreground focus", PermissionLevel.SYSTEM)

    async def execute(self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        title = parameters.get("title_or_hwnd")
        req = DesktopActionRequest(action_type=DesktopActionType.FOCUS_WINDOW, window_title_or_hwnd=title)
        res = await desktop_manager.execute_action(req)
        return {"status": res.status.value, "result": res.result}


class DesktopClickTool(BaseDesktopTool):
    def __init__(self) -> None:
        super().__init__("desktop.click", "Performs mouse click at screen coordinates (x, y)", PermissionLevel.SYSTEM)

    async def execute(self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        x, y = parameters.get("x"), parameters.get("y")
        req = DesktopActionRequest(action_type=DesktopActionType.CLICK, x=x, y=y)
        res = await desktop_manager.execute_action(req)
        return {"status": res.status.value, "result": res.result}


class DesktopDoubleClickTool(BaseDesktopTool):
    def __init__(self) -> None:
        super().__init__("desktop.double_click", "Performs mouse double-click at screen coordinates", PermissionLevel.SYSTEM)

    async def execute(self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        x, y = parameters.get("x"), parameters.get("y")
        req = DesktopActionRequest(action_type=DesktopActionType.DOUBLE_CLICK, x=x, y=y)
        res = await desktop_manager.execute_action(req)
        return {"status": res.status.value, "result": res.result}


class DesktopRightClickTool(BaseDesktopTool):
    def __init__(self) -> None:
        super().__init__("desktop.right_click", "Performs right-click at screen coordinates", PermissionLevel.SYSTEM)

    async def execute(self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        x, y = parameters.get("x"), parameters.get("y")
        req = DesktopActionRequest(action_type=DesktopActionType.RIGHT_CLICK, x=x, y=y)
        res = await desktop_manager.execute_action(req)
        return {"status": res.status.value, "result": res.result}


class DesktopDragTool(BaseDesktopTool):
    def __init__(self) -> None:
        super().__init__("desktop.drag", "Performs mouse drag and drop from start to end coordinates", PermissionLevel.SYSTEM)

    async def execute(self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        req = DesktopActionRequest(action_type=DesktopActionType.DRAG, parameters=parameters)
        res = await desktop_manager.execute_action(req)
        return {"status": res.status.value, "result": res.result}


class DesktopScrollTool(BaseDesktopTool):
    def __init__(self) -> None:
        super().__init__("desktop.scroll", "Performs mouse wheel scroll delta", PermissionLevel.SYSTEM)

    async def execute(self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        req = DesktopActionRequest(action_type=DesktopActionType.SCROLL, parameters=parameters)
        res = await desktop_manager.execute_action(req)
        return {"status": res.status.value, "result": res.result}


class DesktopTypeTool(BaseDesktopTool):
    def __init__(self) -> None:
        super().__init__("desktop.type", "Types text string into focused desktop control", PermissionLevel.SYSTEM)

    async def execute(self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        text = parameters.get("text", "")
        req = DesktopActionRequest(action_type=DesktopActionType.TYPE, text_content=text)
        res = await desktop_manager.execute_action(req)
        return {"status": res.status.value, "result": res.result}


class DesktopHotkeyTool(BaseDesktopTool):
    def __init__(self) -> None:
        super().__init__("desktop.hotkey", "Sends key combination shortcut (e.g. 'Ctrl+C', 'Alt+Tab')", PermissionLevel.SYSTEM)

    async def execute(self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        hk = parameters.get("hotkey", "Enter")
        req = DesktopActionRequest(action_type=DesktopActionType.HOTKEY, hotkey_combination=hk)
        res = await desktop_manager.execute_action(req)
        return {"status": res.status.value, "result": res.result}


class DesktopClipboardTool(BaseDesktopTool):
    def __init__(self) -> None:
        super().__init__("desktop.clipboard", "Reads or writes text from system clipboard", PermissionLevel.WRITE)

    async def execute(self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        text = parameters.get("text")
        act = DesktopActionType.CLIPBOARD_PASTE if text else DesktopActionType.CLIPBOARD_READ
        req = DesktopActionRequest(action_type=act, text_content=text)
        res = await desktop_manager.execute_action(req)
        return {"status": res.status.value, "result": res.result}


class DesktopScreenshotTool(BaseDesktopTool):
    def __init__(self) -> None:
        super().__init__("desktop.screenshot", "Captures desktop screen display or region screenshot", PermissionLevel.READ_ONLY)

    async def execute(self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        req = DesktopActionRequest(action_type=DesktopActionType.SCREENSHOT, parameters=parameters)
        res = await desktop_manager.execute_action(req)
        return {"status": res.status.value, "result": res.result}


class DesktopOCRTool(BaseDesktopTool):
    def __init__(self) -> None:
        super().__init__("desktop.ocr", "Performs OCR text extraction on screen capture display", PermissionLevel.READ_ONLY)

    async def execute(self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        req = DesktopActionRequest(action_type=DesktopActionType.OCR)
        res = await desktop_manager.execute_action(req)
        return {"status": res.status.value, "result": res.result}


class DesktopWaitTool(BaseDesktopTool):
    def __init__(self) -> None:
        super().__init__("desktop.wait", "Pauses desktop execution for specified wait duration in seconds", PermissionLevel.READ_ONLY)

    async def execute(self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        import asyncio
        sec = float(parameters.get("seconds", 1.0))
        await asyncio.sleep(sec)
        return {"status": "SUCCESS", "result": {"waited_seconds": sec}}


class DesktopListWindowsTool(BaseDesktopTool):
    def __init__(self) -> None:
        super().__init__("desktop.list_windows", "Lists active desktop window descriptors", PermissionLevel.READ_ONLY)

    async def execute(self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        req = DesktopActionRequest(action_type=DesktopActionType.LIST_WINDOWS)
        res = await desktop_manager.execute_action(req)
        return {"status": res.status.value, "result": res.result}


class DesktopListProcessesTool(BaseDesktopTool):
    def __init__(self) -> None:
        super().__init__("desktop.list_processes", "Lists running system application processes", PermissionLevel.READ_ONLY)

    async def execute(self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        req = DesktopActionRequest(action_type=DesktopActionType.LIST_PROCESSES)
        res = await desktop_manager.execute_action(req)
        return {"status": res.status.value, "result": res.result}


class DesktopActivateWindowTool(BaseDesktopTool):
    def __init__(self) -> None:
        super().__init__("desktop.activate_window", "Activates and restores window handle to foreground", PermissionLevel.SYSTEM)

    async def execute(self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        title = parameters.get("title_or_hwnd")
        req = DesktopActionRequest(action_type=DesktopActionType.ACTIVATE_WINDOW, window_title_or_hwnd=title)
        res = await desktop_manager.execute_action(req)
        return {"status": res.status.value, "result": res.result}


class DesktopResizeWindowTool(BaseDesktopTool):
    def __init__(self) -> None:
        super().__init__("desktop.resize_window", "Resizes window dimensions (width, height)", PermissionLevel.SYSTEM)

    async def execute(self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        req = DesktopActionRequest(action_type=DesktopActionType.RESIZE_WINDOW, parameters=parameters)
        res = await desktop_manager.execute_action(req)
        return {"status": res.status.value, "result": res.result}


class DesktopMoveWindowTool(BaseDesktopTool):
    def __init__(self) -> None:
        super().__init__("desktop.move_window", "Moves window position to (x, y) coordinates", PermissionLevel.SYSTEM)

    async def execute(self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        req = DesktopActionRequest(action_type=DesktopActionType.MOVE_WINDOW, parameters=parameters)
        res = await desktop_manager.execute_action(req)
        return {"status": res.status.value, "result": res.result}
