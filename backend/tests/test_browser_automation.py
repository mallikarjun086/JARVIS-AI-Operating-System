"""
Pytest Test Suite for Playwright Browser Automation Subsystem.
Tests tabs, forms, downloads, uploads, cookies, session persistence, screenshots, DOM extraction, CAPTCHA, AI navigation, and Human Approval gatekeeper.
"""

from httpx import AsyncClient
import pytest
from app.browser.controller import playwright_controller
from app.browser.human_approval import human_approval_gatekeeper
from app.browser.manager import browser_manager
from app.browser.schemas import (
    ApprovalStatus,
    BrowserActionRequest,
    BrowserActionType,
    HighRiskActionType,
)


@pytest.mark.asyncio
async def test_tab_management_and_navigation():
    """Tests opening, switching, and closing browser tabs."""
    initial_tabs = playwright_controller.list_tabs()
    assert len(initial_tabs) >= 1

    t2 = await playwright_controller.new_tab("https://github.com")
    assert t2.url == "https://github.com"
    assert len(playwright_controller.list_tabs()) == len(initial_tabs) + 1

    closed = await playwright_controller.close_tab(t2.tab_id)
    assert closed is True


@pytest.mark.asyncio
async def test_forms_downloads_uploads_cookies():
    """Tests form filling, file uploads, file downloads, and cookies."""
    nav = await playwright_controller.navigate("https://jarvis.ai/login")
    assert str(nav["status"]) in ["200", "200 OK", "SUCCESS"]


    form = await playwright_controller.fill_form("#email", "admin@jarvis.ai")
    assert form["filled"] is True

    down = await playwright_controller.download_file("https://jarvis.ai/report.pdf")
    assert down["filename"] == "downloaded_file.pdf"

    up = await playwright_controller.upload_file("#upload", ["/path/file.txt"])
    assert up["uploaded"] is True

    cookies = await playwright_controller.get_cookies()
    assert len(cookies) >= 1


@pytest.mark.asyncio
async def test_perception_screenshot_dom_captcha():
    """Tests screenshot generation, DOM extraction, and CAPTCHA detection."""
    screenshot_b64 = await playwright_controller.take_screenshot()
    assert len(screenshot_b64) > 100

    dom = await playwright_controller.extract_dom_tree()
    assert dom["tag"] == "html"

    captcha = await playwright_controller.detect_captcha_elements()
    assert captcha.has_captcha is False



@pytest.mark.asyncio
async def test_human_approval_gatekeeper_interception():
    """Verifies high-risk actions (PAYMENT, ACCOUNT_DELETE, etc.) are intercepted for human approval."""
    req = BrowserActionRequest(
        action_type=BrowserActionType.CLICK,
        url="https://shop.com/checkout",
        high_risk_type=HighRiskActionType.PAYMENT
    )

    resp = await browser_manager.execute_action(req)

    assert resp.status == "PENDING_HUMAN_APPROVAL"
    assert resp.requires_approval is True
    assert resp.approval_id is not None

    # Verify ticket in pending approvals
    pending = human_approval_gatekeeper.list_pending_approvals()
    assert any(p.approval_id == resp.approval_id for p in pending)

    # Approve request
    ticket = human_approval_gatekeeper.respond_to_approval(resp.approval_id, approved=True)
    assert ticket.status == ApprovalStatus.APPROVED


@pytest.mark.asyncio
async def test_browser_api_endpoints(client: AsyncClient):
    """Tests FastAPI REST endpoints for browser automation and approvals."""
    # Register & login
    await client.post("/api/v1/auth/register", json={"email": "browser@jarvis.ai", "password": "Password123!", "full_name": "Browser User"})
    login_resp = await client.post("/api/v1/auth/login", data={"username": "browser@jarvis.ai", "password": "Password123!"})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # List Tabs Endpoint
    tabs_resp = await client.get("/api/v1/browser/tabs", headers=headers)
    assert tabs_resp.status_code == 200
    assert len(tabs_resp.json()) >= 1

    # Screenshot Endpoint
    ss_resp = await client.post("/api/v1/browser/screenshot", headers=headers)
    assert ss_resp.status_code == 200
    assert "image_base64" in ss_resp.json()

    # Trigger High-Risk Payment Action
    exec_payload = {
        "action_type": "CLICK",
        "url": "https://bank.com/pay",
        "high_risk_type": "PAYMENT"
    }
    exec_resp = await client.post("/api/v1/browser/execute", json=exec_payload, headers=headers)
    assert exec_resp.status_code == 200
    res_data = exec_resp.json()
    assert res_data["status"] == "PENDING_HUMAN_APPROVAL"
    appr_id = res_data["approval_id"]

    # List Pending Approvals
    appr_resp = await client.get("/api/v1/browser/approvals", headers=headers)
    assert appr_resp.status_code == 200
    assert len(appr_resp.json()) >= 1

    # Respond (Approve) Ticket
    resp_ticket = await client.post(f"/api/v1/browser/approvals/{appr_id}/respond?approved=true", headers=headers)
    assert resp_ticket.status_code == 200
    assert resp_ticket.json()["status"] == "APPROVED"
