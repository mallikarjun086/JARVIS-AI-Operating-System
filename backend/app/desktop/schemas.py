"""
Pydantic Schemas for Enterprise Desktop Automation Engine (Sprint 7 & 7.1).
Defines Window states, Action Queue statuses, UI nodes, UI snapshots, tool metadata, display info, and requests.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, Field, ConfigDict
from app.tools.schemas import PermissionLevel


class WindowState(str, Enum):
    """10 Lifecycle states for Window State Machine."""
    CREATED = "CREATED"
    OPENING = "OPENING"
    READY = "READY"
    ACTIVE = "ACTIVE"
    BACKGROUND = "BACKGROUND"
    MINIMIZED = "MINIMIZED"
    MAXIMIZED = "MAXIMIZED"
    SUSPENDED = "SUSPENDED"
    CLOSED = "CLOSED"
    ERROR = "ERROR"


class ActionQueueStatus(str, Enum):
    """Traceable action queue statuses."""
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class HighRiskDesktopActionType(str, Enum):
    REGISTRY_EDIT = "REGISTRY_EDIT"
    ADMIN_APP_LAUNCH = "ADMIN_APP_LAUNCH"
    FILE_DELETE = "FILE_DELETE"
    SYSTEM_SETTING_CHANGE = "SYSTEM_SETTING_CHANGE"
    CREDENTIAL_DIALOG = "CREDENTIAL_DIALOG"
    SENSITIVE_CLIPBOARD = "SENSITIVE_CLIPBOARD"
    APP_INSTALLATION = "APP_INSTALLATION"
    APP_REMOVAL = "APP_REMOVAL"
    SYSTEM_SHUTDOWN = "SYSTEM_SHUTDOWN"
    SYSTEM_RESTART = "SYSTEM_RESTART"
    DRIVER_INSTALLATION = "DRIVER_INSTALLATION"
    ADMIN_PROMPT = "ADMIN_PROMPT"


class DesktopActionType(str, Enum):
    LAUNCH_APP = "LAUNCH_APP"
    CLOSE_APP = "CLOSE_APP"
    FIND_WINDOW = "FIND_WINDOW"
    FOCUS_WINDOW = "FOCUS_WINDOW"
    ACTIVATE_WINDOW = "ACTIVATE_WINDOW"
    MINIMIZE_WINDOW = "MINIMIZE_WINDOW"
    MAXIMIZE_WINDOW = "MAXIMIZE_WINDOW"
    RESIZE_WINDOW = "RESIZE_WINDOW"
    MOVE_WINDOW = "MOVE_WINDOW"
    CLICK = "CLICK"
    DOUBLE_CLICK = "DOUBLE_CLICK"
    RIGHT_CLICK = "RIGHT_CLICK"
    DRAG = "DRAG"
    SCROLL = "SCROLL"
    TYPE = "TYPE"
    HOTKEY = "HOTKEY"
    CLIPBOARD_COPY = "CLIPBOARD_COPY"
    CLIPBOARD_PASTE = "CLIPBOARD_PASTE"
    CLIPBOARD_READ = "CLIPBOARD_READ"
    SCREENSHOT = "SCREENSHOT"
    OCR = "OCR"
    WAIT = "WAIT"
    LIST_WINDOWS = "LIST_WINDOWS"
    LIST_PROCESSES = "LIST_PROCESSES"


class DisplayInfo(BaseModel):
    """Monitor display descriptor."""
    display_index: int
    name: str
    width: int
    height: int
    dpi_scaling: float = 1.0
    is_primary: bool = True


class ProcessInfo(BaseModel):
    """Running application process descriptor."""
    pid: int
    name: str
    executable_path: str
    cpu_percent: float = 0.0
    memory_mb: float = 0.0
    status: str = "running"


class WindowInfo(BaseModel):
    """Information descriptor for a desktop window."""
    hwnd: int = Field(..., description="Window handle ID")
    title: str = Field(..., description="Window title string")
    process_name: str = Field(default="unknown")
    pid: int = 0
    x: int = 0
    y: int = 0
    width: int = 0
    height: int = 0
    state: WindowState = Field(default=WindowState.READY)
    is_active: bool = False


class UINode(BaseModel):
    """Platform-agnostic UI Accessibility Tree Node."""
    id: str = Field(default_factory=lambda: f"node-{uuid.uuid4().hex[:6]}")
    automation_id: Optional[str] = None
    class_name: Optional[str] = None
    control_type: str = Field(default="Button")
    name: Optional[str] = None
    text: Optional[str] = None
    enabled: bool = True
    visible: bool = True
    focused: bool = False
    bounding_rectangle: Dict[str, int] = Field(default_factory=dict)
    parent_id: Optional[str] = None
    children: List["UINode"] = Field(default_factory=list)


class DesktopUISnapshot(BaseModel):
    """Unified UI Accessibility Tree Snapshot."""
    window_title: str
    hwnd: int
    root_node: UINode
    captured_at: datetime = Field(default_factory=datetime.utcnow)


class OCRBoundingBox(BaseModel):
    """OCR text bounding box descriptor."""
    text: str
    x: int
    y: int
    width: int
    height: int
    confidence: float = 0.95


class OCRResult(BaseModel):
    """OCR text extraction result."""
    extracted_text: str
    boxes: List[OCRBoundingBox] = Field(default_factory=list)


class DesktopToolMetadata(BaseModel):
    """Exposed capability metadata for Desktop Tools."""
    tool_name: str
    version: str = "1.0.0"
    description: str
    permission_level: PermissionLevel
    supported_platforms: List[str] = Field(default_factory=lambda: ["windows"])
    requires_window: bool = True
    requires_focus: bool = True
    estimated_runtime_seconds: float = 1.0
    supports_parallel: bool = False
    supports_rollback: bool = True
    health_status: str = "HEALTHY"


class DesktopActionRequest(BaseModel):
    """Request payload for desktop automation action."""
    action_type: DesktopActionType
    app_name_or_path: Optional[str] = None
    window_title_or_hwnd: Optional[Any] = None
    selector_or_id: Optional[str] = None
    text_content: Optional[str] = None
    x: Optional[int] = None
    y: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    button: Optional[str] = Field(default="left")
    hotkey_combination: Optional[str] = None
    wait_seconds: Optional[float] = Field(default=1.0)
    high_risk_type: Optional[HighRiskDesktopActionType] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)


class DesktopActionResponse(BaseModel):
    """Response payload for desktop automation action."""
    model_config = ConfigDict(from_attributes=True)

    action_id: str = Field(default_factory=lambda: f"dact-{uuid.uuid4().hex[:8]}")
    action_type: DesktopActionType
    status: ActionQueueStatus = ActionQueueStatus.COMPLETED
    result: Optional[Any] = None
    error_message: Optional[str] = None
    requires_approval: bool = False
    approval_id: Optional[str] = None
    executed_at: datetime = Field(default_factory=datetime.utcnow)


class HumanApprovalRequest(BaseModel):
    """Human approval gatekeeper ticket."""
    approval_id: str = Field(default_factory=lambda: f"dappr-{uuid.uuid4().hex[:8]}")
    high_risk_type: HighRiskDesktopActionType
    target_details: Dict[str, Any]
    status: str = "PENDING_APPROVAL"  # PENDING_APPROVAL, APPROVED, REJECTED
    requested_at: datetime = Field(default_factory=datetime.utcnow)
    responded_at: Optional[datetime] = None
