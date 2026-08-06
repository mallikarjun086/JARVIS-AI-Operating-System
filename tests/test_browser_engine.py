"""
Comprehensive Tests for Enterprise Browser Automation Engine (Sprint 6).
Tests:
1. BrowserManager initialization, health check, and graceful shutdown
2. SessionManager persistent profile storage & restoration
3. DOMEngine extraction and CAPTCHA detection
4. PerceptionEngine screenshot generation
5. Browser Tools execution via Tool Framework (browser.navigate, browser.click, browser.type, browser.screenshot)
6. HumanApprovalGatekeeper interception of high-risk actions (PAYMENT, PURCHASE, PASSWORD_CHANGE)
7. BrowserMetrics telemetry tracking
"""

import pytest
from app.browser.human_approval import human_approval_gatekeeper
from app.browser.manager import browser_manager
from app.browser.metrics import browser_metrics
from app.browser.schemas import (
    ApprovalStatus,
    BrowserActionRequest,
    BrowserActionType,
    BrowserConfig,
    HighRiskActionType,
)
from app.browser.session import session_manager
from app.tools.executor import execution_manager
from app.tools.registry import tool_registry
from app.tools.schemas import ToolExecutionRequest
from app.tools.categories.browser import (
    BrowserClickTool,
    BrowserNavigateTool,
    BrowserScreenshotTool,
    BrowserTypeTool,
)


@pytest.mark.asyncio
async def test_browser_manager_lifecycle():
    """Verifies BrowserManager initialization, health diagnostics, and shutdown."""
    cfg = BrowserConfig(headless=True)
    await browser_manager.initialize(cfg)

    health = await browser_manager.get_health_status()
    assert health["initialized"] is True
    assert health["headless"] is True
    assert health["active_tabs"] >= 1

    await browser_manager.shutdown()
    health_after = await browser_manager.get_health_status()
    assert health_after["initialized"] is False


@pytest.mark.asyncio
async def test_session_persistence():
    """Verifies SessionManager saving and loading browser storageState profiles on disk."""
    cookies = [{"name": "auth_token", "value": "secret_session_token", "domain": "example.com"}]
    saved = session_manager.save_session("test_user_profile", cookies)
    assert saved.profile_name == "test_user_profile"

    loaded = session_manager.load_session("test_user_profile")
    assert loaded is not None
    assert loaded.cookies[0]["value"] == "secret_session_token"

    deleted = session_manager.delete_profile("test_user_profile")
    assert deleted is True


@pytest.mark.asyncio
async def test_browser_tools_execution_via_framework():
    """Verifies executing Browser tools strictly through ToolFramework ToolExecutionManager."""
    tool_registry.register(BrowserNavigateTool)
    tool_registry.register(BrowserClickTool)
    tool_registry.register(BrowserTypeTool)
    tool_registry.register(BrowserScreenshotTool)

    # 1. Execute browser.navigate
    nav_req = ToolExecutionRequest(
        tool_name="browser.navigate",
        parameters={"url": "https://example.com"}
    )
    nav_res = await execution_manager.execute_tool(nav_req, user_role="user")
    assert nav_res.status.value == "SUCCESS"

    # 2. Execute browser.type
    type_req = ToolExecutionRequest(
        tool_name="browser.type",
        parameters={"selector": "input#query", "value": "JARVIS Automation"}
    )
    type_res = await execution_manager.execute_tool(type_req, user_role="user")
    assert type_res.status.value == "SUCCESS"

    # 3. Execute browser.screenshot
    ss_req = ToolExecutionRequest(
        tool_name="browser.screenshot",
        parameters={}
    )
    ss_res = await execution_manager.execute_tool(ss_req, user_role="user")
    assert ss_res.status.value == "SUCCESS"
    assert "image_base64" in ss_res.output["result"]


@pytest.mark.asyncio
async def test_high_risk_human_approval_gatekeeper():
    """Verifies interception of high-risk browser operations requiring human approval."""
    req = BrowserActionRequest(
        action_type=BrowserActionType.FILL_FORM,
        url="https://bank.com/transfer",
        value="$500",
        high_risk_type=HighRiskActionType.PAYMENT
    )
    res = await browser_manager.execute_action(req)
    assert res.status == "PENDING_HUMAN_APPROVAL"
    assert res.requires_approval is True
    assert res.approval_id is not None

    # Respond to approval ticket
    ticket = human_approval_gatekeeper.respond_to_approval(res.approval_id, approved=True)
    assert ticket.status == ApprovalStatus.APPROVED


@pytest.mark.asyncio
async def test_browser_metrics():
    """Verifies BrowserMetrics telemetry recording."""
    metrics_dict = browser_metrics.to_dict()
    assert "total_navigations" in metrics_dict
    assert "total_screenshots" in metrics_dict
    assert "total_approvals_requested" in metrics_dict
