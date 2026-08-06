"""
Human Approval Gatekeeper Engine.
Intercepts high-risk browser actions (Payments, Purchases, Email Sending, Account Deletion)
and halts execution until human operator authorization is granted.
"""

from datetime import datetime
from typing import Dict, List, Optional
from app.browser.schemas import ApprovalStatus, HighRiskActionType, HumanApprovalRequest


class HumanApprovalGatekeeper:
    """Gatekeeper intercepting high-risk automation operations requiring human confirmation."""

    def __init__(self) -> None:
        self._pending_approvals: Dict[str, HumanApprovalRequest] = {}

    def create_approval_request(
        self,
        high_risk_type: HighRiskActionType,
        target_details: Dict
    ) -> HumanApprovalRequest:
        """Creates a pending human approval ticket."""
        ticket = HumanApprovalRequest(
            high_risk_type=high_risk_type,
            target_details=target_details,
            status=ApprovalStatus.PENDING_APPROVAL
        )
        self._pending_approvals[ticket.approval_id] = ticket
        return ticket

    def respond_to_approval(self, approval_id: str, approved: bool) -> Optional[HumanApprovalRequest]:
        """Responds to a pending approval ticket (APPROVED or REJECTED)."""
        ticket = self._pending_approvals.get(approval_id)
        if not ticket:
            return None

        ticket.status = ApprovalStatus.APPROVED if approved else ApprovalStatus.REJECTED
        ticket.responded_at = datetime.utcnow()
        return ticket

    def get_approval(self, approval_id: str) -> Optional[HumanApprovalRequest]:
        """Fetches approval ticket status by ID."""
        return self._pending_approvals.get(approval_id)

    def list_pending_approvals(self) -> List[HumanApprovalRequest]:
        """Lists active pending human approval requests."""
        return [
            t for t in self._pending_approvals.values()
            if t.status == ApprovalStatus.PENDING_APPROVAL
        ]


human_approval_gatekeeper = HumanApprovalGatekeeper()
