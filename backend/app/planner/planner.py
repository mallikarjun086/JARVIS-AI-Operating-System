"""
Backward-compatible module import bridge for Planner Kernel.
"""

from app.planner.engine import TaskPlannerEngine, task_planner
from app.planner.decomposer import TaskDecomposer, intent_decomposer

TaskPlanner = TaskPlannerEngine
planner_engine = task_planner
