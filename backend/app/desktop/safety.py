"""
Safety Gatekeeper & High-Risk Interception Engine.
Intercepts sensitive desktop operations (Registry editing, Admin apps, File deletion, System settings, Credential dialogs, Shutdown) and holds for human authorization.
"""

from datetime import datetime
from typing import Dict, List, Optional
import structlog
from app.desktop.schemas import HighRiskDesktopActionType, HumanApprovalRequest

logger = structlog.get_logger(__name__)


class DesktopSafetyGatekeeper:
    """Gatekeeper intercepting high-risk native desktop operations requiring human authorization."""

    def __init__(self) -> None:
        self._pending_approvals: Dict[str, HumanApprovalRequest] = {}

    def create_approval_request(
        self,
        high_risk_type: HighRiskDesktopActionType,
        target_details: Dict
    ) -> HumanApprovalRequest:
        """Creates a pending human approval ticket."""
        ticket = HumanApprovalRequest(
            high_risk_type=high_risk_type,
            target_details=target_details,
            status="PENDING_APPROVAL"
        )
        self._pending_approvals[ticket.approval_id] = ticket
        logger.warning("Created high-risk desktop approval ticket", approval_id=ticket.approval_id, type=high_risk_type.value)
        return ticket

    def respond_to_approval(self, approval_id: str, approved: bool) -> Optional[HumanApprovalRequest]:
        """Responds to pending approval ticket."""
        ticket = self._pending_approvals.get(approval_id)
        if not ticket:
            return None

        ticket.status = "APPROVED" if approved else "REJECTED"
        ticket.responded_at = datetime.utcnow()
        logger.info("Responded to desktop approval ticket", approval_id=approval_id, approved=approved)
        return ticket

    def evaluate_action_risk(self, action_type: str, app_name_or_path: Optional[str] = None, parameters: Optional[Dict] = None) -> Optional[HighRiskDesktopActionType]:
        """Auto-detects high risk actions requiring human approval."""
        target = (app_name_or_path or "").lower()
        params = str(parameters or {}).lower()

        if "regedit" in target or "registry" in params:
            return HighRiskDesktopActionType.REGISTRY_EDIT
        if "shutdown" in target or "shutdown" in params:
            return HighRiskDesktopActionType.SYSTEM_SHUTDOWN
        if "restart" in target or "reboot" in params:
            return HighRiskDesktopActionType.SYSTEM_RESTART
        if "installer" in target or "setup.exe" in target or "msiexec" in target:
            return HighRiskDesktopActionType.APP_INSTALLATION
        if "uninstall" in target or "remove" in params:
            return HighRiskDesktopActionType.APP_REMOVAL
        if "credential" in target or "password" in params or "login" in params:
            return HighRiskDesktopActionType.CREDENTIAL_DIALOG
        if "driver" in target or "pnputil" in target:
            return HighRiskDesktopActionType.DRIVER_INSTALLATION
        if "runas" in target or "sudo" in target or "admin" in target:
            return HighRiskDesktopActionType.ADMIN_PROMPT
        if "control.exe" in target or "sysdm.cpl" in target:
            return HighRiskDesktopActionType.SYSTEM_SETTING_CHANGE
        return None

    def list_pending_approvals(self) -> List[HumanApprovalRequest]:
        """Lists active pending human approval requests."""
        return [t for t in self._pending_approvals.values() if t.status == "PENDING_APPROVAL"]


desktop_safety_gatekeeper = DesktopSafetyGatekeeper()
