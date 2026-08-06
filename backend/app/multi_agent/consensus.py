"""
Multi-Agent Consensus Engine (Sprint 9 Step 11).
Evaluates agent verification signatures and votes (majority voting, confidence scoring, weighted voting, tie resolution, human escalation).
"""

from typing import List, Optional
import structlog

from app.multi_agent.schemas import AgentRole, ConsensusResult, ConsensusVote, SubTaskSpec

logger = structlog.get_logger(__name__)


class ConsensusEngine:
    """Multi-Agent Consensus Voting and Quality Gatekeeper Engine."""

    @classmethod
    def evaluate_subtask_consensus(
        cls,
        subtasks: List[SubTaskSpec],
        votes: Optional[List[ConsensusVote]] = None
    ) -> ConsensusResult:
        """
        Evaluates task execution results and agent votes:
        1. Aggregates verification signatures from Verifier / Quality agents.
        2. Calculates weighted confidence score.
        3. Escalates to human approval if confidence < 0.70 or votes are tied.
        """
        if not votes:
            # Generate default votes based on subtask statuses
            votes = []
            for st in subtasks:
                approved = (st.status.value in ["COMPLETED", "VERIFIED"])
                votes.append(
                    ConsensusVote(
                        agent_id=st.assigned_agent_id or f"agent-{st.assigned_agent or 'unknown'}",
                        role=st.assigned_agent or AgentRole.VERIFIER,
                        approved=approved,
                        confidence_score=0.95 if approved else 0.30,
                        vote_weight=1.5 if st.assigned_agent == AgentRole.VERIFIER else 1.0,
                        reason=st.error_message if not approved else "Passed subtask criteria"
                    )
                )

        pos_count = sum(1 for v in votes if v.approved)
        neg_count = sum(1 for v in votes if not v.approved)
        total = len(votes)

        weighted_pos = sum(v.vote_weight * v.confidence_score for v in votes if v.approved)
        weighted_total = sum(v.vote_weight for v in votes)
        overall_confidence = round(weighted_pos / max(1.0, weighted_total), 2)

        # Tie or low confidence triggers escalation
        escalate = (pos_count == neg_count) or (overall_confidence < 0.70)
        consensus_passed = (pos_count > neg_count) and not escalate

        logger.info(
            "ConsensusEngine evaluated voting",
            passed=consensus_passed,
            confidence=overall_confidence,
            pos_votes=pos_count,
            neg_votes=neg_count,
            escalate=escalate
        )

        return ConsensusResult(
            consensus_passed=consensus_passed,
            overall_confidence=overall_confidence,
            total_votes=total,
            positive_votes=pos_count,
            negative_votes=neg_count,
            escalated_to_human=escalate,
            votes=votes
        )


consensus_engine = ConsensusEngine()
