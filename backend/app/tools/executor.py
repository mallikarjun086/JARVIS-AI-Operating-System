"""
Tool Execution Manager Engine.
Enforces permissions, validation, timeouts, exponential retries, cancellation,
rollback compensation, parallel/sequential batching, audit logging, and metrics telemetry.
"""

import asyncio
import time
import uuid
from typing import Any, Dict, List, Optional
import structlog

from app.tools.audit import audit_logger
from app.tools.factory import tool_factory
from app.tools.metrics import tool_metrics
from app.tools.permissions import permission_manager
from app.tools.registry import tool_registry
from app.tools.schemas import ExecutionStatus, ToolExecutionRequest, ToolExecutionResult
from app.tools.validator import validator_engine

logger = structlog.get_logger(__name__)


class ToolExecutionManager:
    """
    Central execution layer for all tool calls in the AI Operating System.
    Guarantees: Permission Guard -> Schema Validation -> Timeout/Retry -> Rollback on Error -> Audit Log.
    """

    @classmethod
    async def execute_tool(
        cls,
        req: ToolExecutionRequest,
        context: Dict[str, Any] | None = None,
        user_role: str = "user",
        user_id: Optional[str] = None
    ) -> ToolExecutionResult:
        """
        Executes a single tool request end-to-end.
        """
        context = context or {}
        request_id = req.request_id or str(uuid.uuid4())
        workflow_id = req.workflow_id
        start_time = time.time()

        # 1. Rate Limit Check
        if not permission_manager.check_rate_limit(req.tool_name, user_id=user_id):
            elapsed = round(time.time() - start_time, 4)
            res = ToolExecutionResult(
                request_id=request_id,
                workflow_id=workflow_id,
                tool_name=req.tool_name,
                status=ExecutionStatus.PERMISSION_DENIED,
                error_message="Rate limit exceeded for tool execution.",
                execution_time_seconds=elapsed
            )
            tool_metrics.record_execution(req.tool_name, "PERMISSION_DENIED", elapsed)
            return res

        # 2. Lookup Tool in Registry & Factory
        tool = await tool_factory.get_or_create(req.tool_name)
        if not tool:
            elapsed = round(time.time() - start_time, 4)
            res = ToolExecutionResult(
                request_id=request_id,
                workflow_id=workflow_id,
                tool_name=req.tool_name,
                status=ExecutionStatus.FAILED,
                error_message=f"Tool '{req.tool_name}' not found in global registry.",
                execution_time_seconds=elapsed
            )
            tool_metrics.record_execution(req.tool_name, "FAILED", elapsed)
            return res

        # 3. Security & Permission Check
        allowed, denial_reason = permission_manager.verify_permission(
            tool=tool,
            user_role=user_role,
            approval_granted=req.approval_granted
        )

        if not allowed:
            elapsed = round(time.time() - start_time, 4)
            res = ToolExecutionResult(
                request_id=request_id,
                workflow_id=workflow_id,
                tool_name=tool.name,
                status=ExecutionStatus.PERMISSION_DENIED,
                error_message=denial_reason,
                execution_time_seconds=elapsed
            )
            audit_logger.log_execution(
                tool_name=tool.name,
                user_role=user_role,
                permission_level=tool.permission_level,
                parameters=req.parameters,
                status=ExecutionStatus.PERMISSION_DENIED,
                execution_time_seconds=elapsed,
                request_id=request_id,
                workflow_id=workflow_id,
                user_id=user_id,
                error_message=denial_reason
            )
            tool_metrics.record_execution(tool.name, "PERMISSION_DENIED", elapsed)
            return res

        # 4. Parameter Validation Engine
        try:
            validated_input = validator_engine.validate_input(tool, req.parameters)
            input_dict = validated_input.model_dump()
        except ValueError as ve:
            elapsed = round(time.time() - start_time, 4)
            res = ToolExecutionResult(
                request_id=request_id,
                workflow_id=workflow_id,
                tool_name=tool.name,
                status=ExecutionStatus.VALIDATION_ERROR,
                error_message=str(ve),
                execution_time_seconds=elapsed
            )
            audit_logger.log_execution(
                tool_name=tool.name,
                user_role=user_role,
                permission_level=tool.permission_level,
                parameters=req.parameters,
                status=ExecutionStatus.VALIDATION_ERROR,
                execution_time_seconds=elapsed,
                request_id=request_id,
                workflow_id=workflow_id,
                user_id=user_id,
                error_message=str(ve)
            )
            tool_metrics.record_execution(tool.name, "VALIDATION_ERROR", elapsed)
            return res

        timeout = req.timeout_seconds or tool.timeout_seconds
        max_retries = req.max_retries if req.max_retries is not None else tool.max_retries

        retry_count = 0
        last_error: Optional[Exception] = None
        last_error_msg = ""
        rolled_back = False

        # 5. Execution Loop with Timeouts, Retries & Cancellation
        for attempt in range(1 + max_retries):
            try:
                logger.info("tool_execution_start", tool=tool.name, attempt=attempt, request_id=request_id)

                raw_output = await asyncio.wait_for(
                    tool.execute(input_dict, context),
                    timeout=timeout
                )

                # 6. Output Schema Validation
                validated_output = validator_engine.validate_output(tool, raw_output)

                elapsed = round(time.time() - start_time, 4)
                logger.info("tool_execution_success", tool=tool.name, elapsed_seconds=elapsed, retries=retry_count)

                res = ToolExecutionResult(
                    request_id=request_id,
                    workflow_id=workflow_id,
                    tool_name=tool.name,
                    status=ExecutionStatus.SUCCESS,
                    output=validated_output.model_dump(),
                    execution_time_seconds=elapsed,
                    retry_count=retry_count,
                    rolled_back=False,
                    approval_source="user_explicit" if req.approval_granted else "policy_auto"
                )

                audit_logger.log_execution(
                    tool_name=tool.name,
                    user_role=user_role,
                    permission_level=tool.permission_level,
                    parameters=req.parameters,
                    status=ExecutionStatus.SUCCESS,
                    execution_time_seconds=elapsed,
                    retry_count=retry_count,
                    request_id=request_id,
                    workflow_id=workflow_id,
                    user_id=user_id,
                    approval_source=res.approval_source
                )
                tool_metrics.record_execution(tool.name, "SUCCESS", elapsed, retry_count=retry_count)
                return res

            except asyncio.CancelledError:
                last_error_msg = "Execution task was cancelled."
                logger.warning("tool_execution_cancelled", tool=tool.name, request_id=request_id)
                break
            except asyncio.TimeoutError:
                last_error_msg = f"Execution timed out after {timeout} seconds."
                last_error = TimeoutError(last_error_msg)
                logger.warning("tool_timeout", tool=tool.name, attempt=attempt, timeout=timeout)
            except Exception as e:
                last_error = e
                last_error_msg = str(e)
                logger.warning("tool_execution_error", tool=tool.name, attempt=attempt, error=last_error_msg)

            retry_count = attempt

            if attempt < max_retries:
                backoff_delay = 0.1 * (2 ** attempt)
                await asyncio.sleep(backoff_delay)

        # Execution Failed — Trigger Rollback compensation logic
        elapsed = round(time.time() - start_time, 4)
        if last_error:
            try:
                rolled_back = await tool.rollback(input_dict, context, last_error)
            except Exception as rb_err:
                logger.error("Tool rollback failed", tool=tool.name, error=str(rb_err))
                rolled_back = False

        status_code = ExecutionStatus.CANCELLED if "cancelled" in last_error_msg else (
            ExecutionStatus.TIMEOUT if "timed out" in last_error_msg else ExecutionStatus.FAILED
        )

        res = ToolExecutionResult(
            request_id=request_id,
            workflow_id=workflow_id,
            tool_name=tool.name,
            status=status_code,
            error_message=f"Tool execution failed after {retry_count} retries. Error: {last_error_msg}",
            execution_time_seconds=elapsed,
            retry_count=retry_count,
            rolled_back=rolled_back
        )

        audit_logger.log_execution(
            tool_name=tool.name,
            user_role=user_role,
            permission_level=tool.permission_level,
            parameters=req.parameters,
            status=status_code,
            execution_time_seconds=elapsed,
            retry_count=retry_count,
            request_id=request_id,
            workflow_id=workflow_id,
            user_id=user_id,
            rolled_back=rolled_back,
            error_message=last_error_msg
        )
        tool_metrics.record_execution(tool.name, status_code.value, elapsed, retry_count=retry_count, rolled_back=rolled_back)
        return res

    @classmethod
    async def execute_parallel(
        cls,
        requests: List[ToolExecutionRequest],
        context: Dict[str, Any] | None = None,
        user_role: str = "user",
        user_id: Optional[str] = None
    ) -> List[ToolExecutionResult]:
        """
        Executes multiple tool requests concurrently in parallel using asyncio.gather.
        """
        tasks = [
            cls.execute_tool(req, context=context, user_role=user_role, user_id=user_id)
            for req in requests
        ]
        return list(await asyncio.gather(*tasks))

    @classmethod
    async def execute_sequential(
        cls,
        requests: List[ToolExecutionRequest],
        context: Dict[str, Any] | None = None,
        user_role: str = "user",
        user_id: Optional[str] = None,
        stop_on_failure: bool = True
    ) -> List[ToolExecutionResult]:
        """
        Executes a sequence of tool requests sequentially, passing intermediate context.
        """
        results = []
        ctx = context or {}
        for req in requests:
            res = await cls.execute_tool(req, context=ctx, user_role=user_role, user_id=user_id)
            results.append(res)
            if stop_on_failure and res.status != ExecutionStatus.SUCCESS:
                break
        return results


execution_manager = ToolExecutionManager()
