"""
Intent Analyzer — Parses natural language goals, extracts entities, constraints, and priorities.
"""

import re
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.planner.schemas import SubTaskPriority


class ParsedIntent(BaseModel):
    """Structured intent representation of user request."""
    category: str = Field(..., description="High-level category (e.g. software_development, system_admin, data_query)")
    primary_goal: str
    entities: Dict[str, Any] = Field(default_factory=dict, description="Extracted entities like framework, repo, path")
    constraints: List[str] = Field(default_factory=list, description="Extracted operational constraints")
    suggested_priority: SubTaskPriority = Field(default=SubTaskPriority.NORMAL)
    confidence_score: float = Field(default=0.95, ge=0.0, le=1.0)


class IntentAnalyzer:
    """Analyzes natural language goals into structured intent objects."""

    @classmethod
    def analyze_intent(cls, goal: str, context: Optional[str] = None) -> ParsedIntent:
        """
        Parses goal text to classify category, extract key entities, constraints, and priority.
        """
        goal_lower = goal.lower()
        entities: Dict[str, Any] = {}
        constraints: List[str] = []

        # 1. Entity Extraction
        if "spring boot" in goal_lower:
            entities["framework"] = "Spring Boot"
            entities["build_tool"] = "Maven"
        if "github" in goal_lower or "git" in goal_lower:
            entities["vcs"] = "Git"
            entities["remote_provider"] = "GitHub"

        # File paths extraction (e.g. "read file requirements.txt")
        file_matches = re.findall(r"[\w\-\./]+\.(?:txt|md|py|java|json|yml|yaml|xml|js|ts)", goal)
        if file_matches:
            entities["target_files"] = file_matches

        # 2. Priority Detection
        priority = SubTaskPriority.NORMAL
        if any(w in goal_lower for w in ("urgent", "critical", "immediately", "asap")):
            priority = SubTaskPriority.CRITICAL
        elif any(w in goal_lower for w in ("high", "important", "priority")):
            priority = SubTaskPriority.HIGH
        elif any(w in goal_lower for w in ("low", "optional", "background")):
            priority = SubTaskPriority.LOW

        # 3. Category Classification
        if "spring" in goal_lower or "code" in goal_lower or "project" in goal_lower or "repo" in goal_lower:
            category = "software_development"
        elif "search" in goal_lower or "find" in goal_lower or "query" in goal_lower:
            category = "information_retrieval"
        else:
            category = "system_automation"

        # 4. Constraint Extraction
        if "without" in goal_lower:
            constraints.append("Negative constraint specified in prompt")
        if "parallel" in goal_lower:
            constraints.append("Optimize for parallel task execution")

        return ParsedIntent(
            category=category,
            primary_goal=goal,
            entities=entities,
            constraints=constraints,
            suggested_priority=priority,
            confidence_score=0.95
        )


intent_analyzer = IntentAnalyzer()
