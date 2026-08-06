"""
Intent Understanding & LLM Task Decomposition Engine.
Converts natural language user goals into granular PlanTask objects mapped to Tool Framework tools.
"""

import json
from typing import List, Optional, Tuple
import structlog

from app.ai.router import llm_router
from app.ai.schemas import LLMMessage, LLMRequest, MessageRole
from app.planner.intent import ParsedIntent, intent_analyzer
from app.planner.schemas import PlanTask, SubTaskPriority
from app.tools.schemas import PermissionLevel

logger = structlog.get_logger(__name__)


class TaskDecomposer:
    """
    Decomposes natural language user goals into atomic PlanTask objects
    strictly mapped to Tool Framework tools.
    """

    @classmethod
    async def decompose_goal(
        cls,
        goal: str,
        context: Optional[str] = None,
        memory_context: Optional[List[str]] = None
    ) -> Tuple[ParsedIntent, List[PlanTask]]:
        """
        Analyzes intent and generates a structured list of PlanTask objects.
        """
        intent = intent_analyzer.analyze_intent(goal, context)
        goal_lower = goal.lower()

        # 1. Pattern matching for standard Spring Boot + GitHub workflow
        if "spring boot" in goal_lower and "github" in goal_lower:
            tasks = [
                PlanTask(
                    task_id="task_1",
                    title="Create Workspace Directory",
                    description="Creates directory for Spring Boot project",
                    tool_required="filesystem.write_file",
                    permission_level=PermissionLevel.WRITE,
                    inputs={"path": "pom.xml", "content": "<project></project>"},
                    outputs_expected={"path": "string"},
                    dependencies=[],
                    priority=SubTaskPriority.HIGH,
                    estimated_runtime_seconds=1.0
                ),
                PlanTask(
                    task_id="task_2",
                    title="Generate Spring Application Code",
                    description="Writes main Spring Boot Application java class",
                    tool_required="filesystem.write_file",
                    permission_level=PermissionLevel.WRITE,
                    inputs={"path": "src/main/java/DemoApplication.java", "content": "package com.example;"},
                    outputs_expected={"path": "string"},
                    dependencies=["task_1"],
                    priority=SubTaskPriority.HIGH,
                    estimated_runtime_seconds=1.5
                ),
                PlanTask(
                    task_id="task_3",
                    title="Generate README Documentation",
                    description="Generates README.md project documentation",
                    tool_required="filesystem.write_file",
                    permission_level=PermissionLevel.WRITE,
                    inputs={"path": "README.md", "content": "# Spring Boot Project"},
                    outputs_expected={"path": "string"},
                    dependencies=["task_1"],  # Parallelizable with task_2!
                    priority=SubTaskPriority.NORMAL,
                    estimated_runtime_seconds=0.5
                ),
                PlanTask(
                    task_id="task_4",
                    title="Check Git Repository Status",
                    description="Runs git status to check workspace status",
                    tool_required="git.status",
                    permission_level=PermissionLevel.READ_ONLY,
                    inputs={"repo_path": "."},
                    outputs_expected={"clean": "bool"},
                    dependencies=["task_2", "task_3"],
                    priority=SubTaskPriority.NORMAL,
                    estimated_runtime_seconds=1.0
                ),
                PlanTask(
                    task_id="task_5",
                    title="Initialize Git & Commit",
                    description="Initializes git repo and creates initial commit",
                    tool_required="terminal.execute_command",
                    permission_level=PermissionLevel.SYSTEM,
                    inputs={"command": "git init && git add . && git commit -m 'Initial commit'"},
                    outputs_expected={"stdout": "string"},
                    dependencies=["task_4"],
                    priority=SubTaskPriority.CRITICAL,

                    estimated_runtime_seconds=2.0
                ),
            ]
            return intent, tasks

        # 2. Generic AI Planner Decomposition
        mem_str = "\n".join(memory_context) if memory_context else "None"
        prompt = f"""Break down the following user goal into granular subtasks.
Goal: {goal}
Memory Context: {mem_str}
Category: {intent.category}

Return JSON array of subtasks matching format:
[
  {{
    "task_id": "task_1",
    "title": "Task title",
    "description": "Task description",
    "tool_required": "filesystem.write_file",
    "permission_level": 1,
    "inputs": {{"path": "file.txt", "content": "hello"}},
    "dependencies": []
  }}
]"""

        req = LLMRequest(
            model="gpt-3.5-turbo",
            messages=[LLMMessage(role=MessageRole.USER, content=prompt)],
            system_prompt="You are an AI Task Planner. Decompose goals into tool-mapped subtasks. Output JSON array only."
        )

        try:
            llm_res = await llm_router.generate_completion(req)
            raw_text = llm_res.content.strip()

            # Attempt JSON parse
            if "```json" in raw_text:
                raw_text = raw_text.split("```json")[1].split("```")[0].strip()
            elif "```" in raw_text:
                raw_text = raw_text.split("```")[1].split("```")[0].strip()

            parsed_list = json.loads(raw_text)
            tasks = [PlanTask.model_validate(t) for t in parsed_list]
            return intent, tasks
        except Exception as e:
            logger.warning("LLM decomposition fallback", error=str(e))
            # Fallback default plan
            tasks = [
                PlanTask(
                    task_id="task_1",
                    title="System Workspace Setup",
                    description=f"Inspect system health for goal: {goal}",
                    tool_required="system.health",
                    permission_level=PermissionLevel.READ_ONLY,
                    inputs={},
                    outputs_expected={"healthy": "bool"},
                    dependencies=[],
                    estimated_runtime_seconds=0.5
                ),
                PlanTask(
                    task_id="task_2",
                    title="Execute Target Action",
                    description=f"Executes target action for goal: {goal}",
                    tool_required="terminal.execute_command",
                    permission_level=PermissionLevel.SYSTEM,
                    inputs={"command": f"echo Executing goal: {goal}"},
                    outputs_expected={"stdout": "string"},
                    dependencies=["task_1"],
                    estimated_runtime_seconds=1.0
                )
            ]
            return intent, tasks


decomposer = TaskDecomposer()
intent_decomposer = decomposer

