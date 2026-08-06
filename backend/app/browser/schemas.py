"""
Pydantic Schemas for Enterprise Playwright Browser Automation Subsystem.
Defines browser configs, DOM element nodes, tab descriptors, session profiles, and action contracts.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, Field, ConfigDict


class HighRiskActionType(str, Enum):
    PAYMENT = "PAYMENT"
    PURCHASE = "PURCHASE"
    EMAIL_SEND = "EMAIL_SEND"
    ACCOUNT_DELETE = "ACCOUNT_DELETE"
    PASSWORD_CHANGE = "PASSWORD_CHANGE"
    SENSITIVE_UPLOAD = "SENSITIVE_UPLOAD"


class ApprovalStatus(str, Enum):
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class BrowserTypeEnum(str, Enum):
    CHROMIUM = "chromium"
    FIREFOX = "firefox"
    WEBKIT = "webkit"


class BrowserActionType(str, Enum):
    OPEN = "OPEN"
    NAVIGATE = "NAVIGATE"
    CLICK = "CLICK"
    DOUBLE_CLICK = "DOUBLE_CLICK"
    HOVER = "HOVER"
    DRAG_AND_DROP = "DRAG_AND_DROP"
    TYPE = "TYPE"
    SELECT = "SELECT"
    WAIT = "WAIT"
    FILL_FORM = "FILL_FORM"
    UPLOAD_FILE = "UPLOAD_FILE"
    DOWNLOAD_FILE = "DOWNLOAD_FILE"
    NEW_TAB = "NEW_TAB"
    CLOSE_TAB = "CLOSE_TAB"
    SWITCH_TAB = "SWITCH_TAB"
    GET_COOKIES = "GET_COOKIES"
    SET_COOKIES = "SET_COOKIES"
    SAVE_SESSION = "SAVE_SESSION"
    RESTORE_SESSION = "RESTORE_SESSION"
    SCREENSHOT = "SCREENSHOT"
    EXTRACT_TEXT = "EXTRACT_TEXT"
    EXTRACT_HTML = "EXTRACT_HTML"
    EXTRACT_DOM = "EXTRACT_DOM"
    DETECT_CAPTCHA = "DETECT_CAPTCHA"
    AI_NAVIGATE = "AI_NAVIGATE"


class BrowserConfig(BaseModel):
    """Configuration for Playwright browser launch and context."""
    browser_type: BrowserTypeEnum = Field(default=BrowserTypeEnum.CHROMIUM)
    headless: bool = Field(default=True, description="True for headless execution, False for headed window")
    slow_mo_ms: float = Field(default=0.0, description="Optional delay between actions in ms")
    user_agent: Optional[str] = Field(default=None)
    viewport_width: int = Field(default=1280)
    viewport_height: int = Field(default=800)
    record_video: bool = Field(default=False)
    session_profile_name: Optional[str] = Field(default=None, description="Persistent profile profile ID")


class TabInfo(BaseModel):
    """Information for an active browser page tab."""
    tab_id: str
    url: str
    title: str
    is_active: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)


class CAPTCHAResult(BaseModel):
    """CAPTCHA detection result payload."""
    has_captcha: bool
    captcha_type: Optional[str] = None  # reCAPTCHA, hCaptcha, Turnstile, Cloudflare
    selector: Optional[str] = None
    confidence: float = 0.0


class DOMElementNode(BaseModel):
    """Tree node representing an extracted HTML DOM element."""
    tag: str
    text: Optional[str] = None
    attributes: Dict[str, str] = Field(default_factory=dict)
    bounding_box: Optional[Dict[str, float]] = None
    is_visible: bool = True
    children: List["DOMElementNode"] = Field(default_factory=list)


class BrowserActionRequest(BaseModel):
    """Request payload for browser automation action."""
    action_type: BrowserActionType
    url: Optional[str] = None
    selector: Optional[str] = None
    xpath: Optional[str] = None
    text_content: Optional[str] = None
    value: Optional[str] = None
    tab_id: Optional[str] = None
    wait_time_seconds: Optional[float] = Field(default=2.0)
    form_data: Dict[str, Any] = Field(default_factory=dict)
    files: List[str] = Field(default_factory=list)
    cookies: List[Dict[str, Any]] = Field(default_factory=list)
    high_risk_type: Optional[HighRiskActionType] = None
    ai_prompt: Optional[str] = Field(default=None, description="Natural language goal for AI navigation")


class BrowserActionResponse(BaseModel):
    """Response payload for browser automation action."""
    model_config = ConfigDict(from_attributes=True)

    action_id: str = Field(default_factory=lambda: f"bact-{uuid.uuid4().hex[:8]}")
    action_type: BrowserActionType
    status: str = "SUCCESS"  # SUCCESS, FAILED, PENDING_HUMAN_APPROVAL, REJECTED
    result: Optional[Any] = None
    error_message: Optional[str] = None
    requires_approval: bool = False
    approval_id: Optional[str] = None
    executed_at: datetime = Field(default_factory=datetime.utcnow)


class HumanApprovalRequest(BaseModel):
    """Human approval gatekeeper ticket."""
    approval_id: str = Field(default_factory=lambda: f"appr-{uuid.uuid4().hex[:8]}")
    high_risk_type: HighRiskActionType
    target_details: Dict[str, Any]
    status: ApprovalStatus = ApprovalStatus.PENDING_APPROVAL
    requested_at: datetime = Field(default_factory=datetime.utcnow)
    responded_at: Optional[datetime] = None


class SessionProfile(BaseModel):
    """Browser session storage profile for login persistence."""
    profile_name: str
    cookies: List[Dict[str, Any]] = Field(default_factory=list)
    local_storage: Dict[str, Any] = Field(default_factory=dict)
    session_storage: Dict[str, Any] = Field(default_factory=dict)
    saved_at: datetime = Field(default_factory=datetime.utcnow)
