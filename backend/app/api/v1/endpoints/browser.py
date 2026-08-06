"""
FastAPI Endpoints for Enterprise Browser Automation Engine.
Endpoints: GET /status, POST /open, POST /close, POST /action, GET /tabs, GET /history, GET /metrics, POST /screenshot, POST /extract-dom, POST /detect-captcha, POST /ai-navigate, GET /approvals, POST /approvals/{id}/respond.
"""

from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.api.deps import get_current_user
from app.browser.human_approval import human_approval_gatekeeper
from app.browser.manager import browser_manager
from app.browser.metrics import browser_metrics
from app.browser.schemas import (
    BrowserActionRequest,
    BrowserActionResponse,
    BrowserActionType,
    CAPTCHAResult,
    HumanApprovalRequest,
    TabInfo,
)
from app.models.user import User

router = APIRouter()


@router.get("/status", summary="Get Browser Manager Health & Status")
async def get_browser_status(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Returns browser manager health diagnostics and active tabs/profiles status."""
    return await browser_manager.get_health_status()


@router.post("/open", response_model=BrowserActionResponse, summary="Open Browser Context / Tab")
async def open_browser(
    url: str = Query(default="about:blank", description="Initial target URL"),
    current_user: User = Depends(get_current_user)
) -> BrowserActionResponse:
    """Opens a new browser tab context."""
    req = BrowserActionRequest(action_type=BrowserActionType.OPEN, url=url)
    return await browser_manager.execute_action(req)


@router.post("/close", response_model=BrowserActionResponse, summary="Close Active Tab")
async def close_browser(
    tab_id: str = Query(default="tab_1", description="Target tab ID"),
    current_user: User = Depends(get_current_user)
) -> BrowserActionResponse:
    """Closes a browser tab or context."""
    req = BrowserActionRequest(action_type=BrowserActionType.CLOSE_TAB, tab_id=tab_id)
    return await browser_manager.execute_action(req)


@router.post("/action", response_model=BrowserActionResponse, summary="Execute Browser Action")
@router.post("/execute", response_model=BrowserActionResponse, summary="Execute Browser Action (Alias)")
async def execute_browser_action(

    req: BrowserActionRequest,
    current_user: User = Depends(get_current_user)
) -> BrowserActionResponse:
    """Executes browser navigation, clicks, typing, downloads, uploads, or high-risk actions."""
    return await browser_manager.execute_action(req)


@router.get("/tabs", response_model=List[TabInfo], summary="List Open Browser Tabs")
async def list_tabs(
    current_user: User = Depends(get_current_user)
) -> List[TabInfo]:
    """Lists active browser tabs."""
    from app.browser.controller import playwright_controller
    return playwright_controller.list_tabs()


@router.get("/metrics", response_model=Dict[str, Any], summary="Get Browser Telemetry Metrics")
async def get_browser_metrics(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Returns telemetry metrics (navigations, DOM extractions, latencies, downloads, uploads, crashes)."""
    return browser_metrics.to_dict()


@router.post("/screenshot", summary="Capture Browser Page Screenshot")
async def capture_screenshot(
    full_page: bool = Query(default=False, description="True for full scrollable page screenshot"),
    current_user: User = Depends(get_current_user)
):
    """Captures page screenshot as Base64 PNG string."""
    from app.browser.controller import playwright_controller
    b64 = await playwright_controller.take_screenshot(full_page=full_page)
    return {"image_base64": b64}


@router.post("/extract-dom", summary="Extract Page DOM Tree")
async def extract_dom(
    current_user: User = Depends(get_current_user)
):
    """Extracts structural HTML DOM element tree."""
    from app.browser.controller import playwright_controller
    return await playwright_controller.extract_dom_tree()


@router.post("/detect-captcha", response_model=CAPTCHAResult, summary="Scan Page for CAPTCHA Elements")
async def detect_captcha(
    current_user: User = Depends(get_current_user)
) -> CAPTCHAResult:
    """Scans page DOM for reCAPTCHA, hCaptcha, Turnstile, or Cloudflare challenge elements."""
    from app.browser.controller import playwright_controller
    return await playwright_controller.detect_captcha_elements()


@router.post("/ai-navigate", summary="AI-Assisted Autonomous Navigation")
async def ai_navigate(
    prompt: str = Query(..., description="Natural language goal prompt"),
    current_user: User = Depends(get_current_user)
):
    """Performs AI-assisted autonomous web navigation."""
    from app.browser.agent import ai_navigator
    return await ai_navigator.navigate_with_ai(prompt)


@router.get("/approvals", response_model=List[HumanApprovalRequest], summary="List Pending Human Approvals")
async def list_pending_approvals(
    current_user: User = Depends(get_current_user)
) -> List[HumanApprovalRequest]:
    """Lists pending human approval tickets for high-risk actions (Payments, Purchases, Password Changes, Account Deletion)."""
    return human_approval_gatekeeper.list_pending_approvals()


@router.post("/approvals/{approval_id}/respond", response_model=HumanApprovalRequest, summary="Approve or Reject High-Risk Action")
async def respond_approval(
    approval_id: str,
    approved: bool = Query(..., description="True to approve execution, False to reject"),
    current_user: User = Depends(get_current_user)
) -> HumanApprovalRequest:
    """Grants authorization or rejects a pending high-risk browser action ticket."""
    ticket = human_approval_gatekeeper.respond_to_approval(approval_id, approved)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Approval ticket '{approval_id}' not found."
        )
    return ticket
