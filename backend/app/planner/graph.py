"""
DAG Dependency Graph Engine — Kahn's Topological Sort & Parallel Layer Detection.
"""

from collections import defaultdict, deque
from typing import Dict, List, Tuple
from app.planner.schemas import DAGValidationResponse, ExecutionBatch, PlanTask


class DependencyGraphEngine:
    """
    Validates Directed Acyclic Graph (DAG) structures and detects parallel execution batch layers.
    """

    @classmethod
    def validate_and_order_dag(cls, subtasks: List[PlanTask]) -> DAGValidationResponse:
        """
        Executes Kahn's Algorithm to validate DAG, detect circular dependencies,
        and generate topological ordering and parallel execution batches.
        """
        task_map: Dict[str, PlanTask] = {t.task_id: t for t in subtasks}
        in_degree: Dict[str, int] = {t.task_id: 0 for t in subtasks}
        graph: Dict[str, List[str]] = defaultdict(list)

        for task in subtasks:
            for dep in task.dependencies:
                if dep in task_map:
                    graph[dep].append(task.task_id)
                    in_degree[task.task_id] += 1

        # Queue of tasks with 0 in-degree (no remaining unsatisfied dependencies)
        queue: deque[str] = deque([t_id for t_id, deg in in_degree.items() if deg == 0])

        topological_order: List[str] = []
        parallel_batches: List[List[str]] = []

        # Process in parallel execution batch layers
        while queue:
            current_batch: List[str] = list(queue)
            parallel_batches.append(current_batch)

            for _ in range(len(current_batch)):
                node = queue.popleft()
                topological_order.append(node)

                for neighbor in graph[node]:
                    in_degree[neighbor] -= 1
                    if in_degree[neighbor] == 0:
                        queue.append(neighbor)

        # Check for circular dependency loops
        is_valid = len(topological_order) == len(subtasks)
        circular_loops: List[List[str]] = []

        if not is_valid:
            cycle_nodes = [t_id for t_id, deg in in_degree.items() if deg > 0]
            circular_loops.append(cycle_nodes)

        return DAGValidationResponse(
            is_valid_dag=is_valid,
            topological_order=topological_order,
            circular_dependencies=circular_loops,
            parallel_batches=parallel_batches
        )

    @classmethod
    def build_execution_batches(cls, subtasks: List[PlanTask]) -> List[ExecutionBatch]:
        """Converts parallel batch layers into ExecutionBatch models."""
        dag_info = cls.validate_and_order_dag(subtasks)
        batches: List[ExecutionBatch] = []

        for idx, task_ids in enumerate(dag_info.parallel_batches, start=1):
            batches.append(
                ExecutionBatch(
                    batch_id=idx,
                    parallel_task_ids=task_ids
                )
            )

        return batches


graph_engine = DependencyGraphEngine()
