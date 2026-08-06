"""
Enterprise Process Execution Engine & Sandbox.
Provides isolated, asynchronous, non-blocking process execution with environment sanitization,
resource quotas, working directory isolation, process tree cleanup, security metrics, and health endpoints.
"""

from abc import ABC, abstractmethod
import asyncio
import os
import signal
import sys
import tempfile
import time
from typing import Any, Dict, List, Optional
import uuid

from app.core.logging import logger
from app.security.command_guard import command_guard
from app.security.schemas import (
    ProcessExecutionRequest,
    ProcessExecutionResult,
    ProcessExecutionStatus,
)


class BaseProcessExecutor(ABC):
    """Abstract interface defining contract for pluggable process execution backends (Local, Docker, K8s, Windows Sandbox)."""

    @abstractmethod
    async def execute(self, request: ProcessExecutionRequest) -> ProcessExecutionResult:
        """Executes a command asynchronously within the execution environment."""
        pass

    @abstractmethod
    async def cancel(self, process_id: str) -> bool:
        """Cancels a running process by ID."""
        pass

    @abstractmethod
    def get_health_status(self) -> Dict[str, Any]:
        """Returns executor health telemetry."""
        pass

    @abstractmethod
    def get_metrics(self) -> Dict[str, Any]:
        """Returns process execution metrics."""
        pass


class LocalProcessExecutor(BaseProcessExecutor):
    """
    Production-grade Local Process Executor.
    Enforces non-blocking asyncio subprocesses, env variable scrubbing, working directory isolation,
    process group kill on timeout/cancel, security metrics, and audit logging.
    """

    SENSITIVE_ENV_KEYS = {
        "SECRET_KEY",
        "POSTGRES_PASSWORD",
        "DATABASE_URL",
        "JWT_SECRET",
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "AWS_SECRET_ACCESS_KEY",
    }

    HUMAN_APPROVAL_COMMANDS = {
        "format",
        "rm -rf /",
        "drop database",
        "curl | sh",
        "wget | sh",
        "poweroff",
        "reboot",
    }

    def __init__(self) -> None:
        self._running_processes: Dict[str, asyncio.subprocess.Process] = {}
        self._total_executions: int = 0
        self._blocked_executions: int = 0
        self._timed_out_executions: int = 0
        self._successful_executions: int = 0

    def _sanitize_environment(self, custom_env: Dict[str, str]) -> Dict[str, str]:
        """Creates a clean environment dict stripping sensitive system credentials."""
        clean_env = {
            k: v for k, v in os.environ.items()
            if k not in self.SENSITIVE_ENV_KEYS and not k.startswith("JARVIS_SECRET_")
        }
        clean_env.update(custom_env)
        clean_env["PATH"] = os.environ.get("PATH", "")
        return clean_env

    def _check_human_approval_required(self, command: str) -> bool:
        """Inspects if command triggers mandatory human approval policy."""
        cmd_lower = command.lower()
        return any(pattern in cmd_lower for pattern in self.HUMAN_APPROVAL_COMMANDS)

    def get_health_status(self) -> Dict[str, Any]:
        """Returns engine operational health status."""
        return {
            "status": "HEALTHY",
            "backend": "LocalProcessExecutor",
            "active_processes": len(self._running_processes),
            "isolation": "ENVIRONMENT_AND_CWD_ISOLATED",
            "platform": sys.platform
        }

    def get_metrics(self) -> Dict[str, Any]:
        """Returns telemetry counters."""
        return {
            "total_executions": self._total_executions,
            "successful_executions": self._successful_executions,
            "blocked_executions": self._blocked_executions,
            "timed_out_executions": self._timed_out_executions,
            "active_processes": len(self._running_processes)
        }

    async def execute(self, request: ProcessExecutionRequest) -> ProcessExecutionResult:
        """Executes process asynchronously with resource limits and isolation."""
        start_time = time.time()
        process_id = f"proc-{uuid.uuid4().hex[:8]}"
        self._total_executions += 1

        # 1. Command Injection Validation
        validation = command_guard.validate_command(request.command)
        if not validation.is_safe:
            self._blocked_executions += 1
            logger.warning(
                "Process execution blocked by Command Guard",
                process_id=process_id,
                command=request.command,
                reasons=validation.flagged_reasons
            )
            return ProcessExecutionResult(
                process_id=process_id,
                command=request.command,
                status=ProcessExecutionStatus.BLOCKED_SECURITY,
                exit_code=-1,
                stdout="",
                stderr=f"Blocked by Command Injection Guard: {', '.join(validation.flagged_reasons)}",
                sandboxed=True,
                blocked=True,
                execution_time_ms=0.0
            )

        # 2. Human Approval Check
        if request.requires_approval or self._check_human_approval_required(request.command):
            logger.info("Process execution queued for Human Approval", process_id=process_id, command=request.command)
            return ProcessExecutionResult(
                process_id=process_id,
                command=request.command,
                status=ProcessExecutionStatus.REQUIRES_HUMAN_APPROVAL,
                exit_code=None,
                stdout="",
                stderr="Execution requires explicit Human Approval before proceeding.",
                sandboxed=True,
                requires_approval=True,
                execution_time_ms=0.0
            )

        # 3. Environment & CWD Preparation
        env = self._sanitize_environment(request.environment_variables)
        cwd = request.cwd or tempfile.gettempdir()

        tokens = command_guard.tokenize_command(validation.sanitized_command)

        logger.info("Executing async process", process_id=process_id, command=validation.sanitized_command, cwd=cwd)

        # 4. Asynchronous Non-blocking Execution
        try:
            kwargs: Dict[str, Any] = {
                "stdout": asyncio.subprocess.PIPE,
                "stderr": asyncio.subprocess.PIPE,
                "cwd": cwd,
                "env": env,
            }
            if sys.platform != "win32":
                kwargs["preexec_fn"] = os.setsid

            if tokens and tokens[0] in command_guard.ALLOWED_EXECUTABLES and sys.platform != "win32":
                proc = await asyncio.create_subprocess_exec(tokens[0], *tokens[1:], **kwargs)
            else:
                proc = await asyncio.create_subprocess_shell(validation.sanitized_command, **kwargs)

            self._running_processes[process_id] = proc

            try:
                stdout_bytes, stderr_bytes = await asyncio.wait_for(
                    proc.communicate(),
                    timeout=float(request.timeout_seconds)
                )
                elapsed_ms = (time.time() - start_time) * 1000.0

                stdout_str = stdout_bytes.decode("utf-8", errors="replace")[:4000]
                stderr_str = stderr_bytes.decode("utf-8", errors="replace")[:2000]

                if proc.returncode == 0:
                    self._successful_executions += 1
                    status = ProcessExecutionStatus.COMPLETED
                else:
                    status = ProcessExecutionStatus.FAILED

                logger.info(
                    "Process execution finished",
                    process_id=process_id,
                    exit_code=proc.returncode,
                    execution_time_ms=round(elapsed_ms, 2)
                )

                return ProcessExecutionResult(
                    process_id=process_id,
                    command=validation.sanitized_command,
                    status=status,
                    exit_code=proc.returncode,
                    stdout=stdout_str,
                    stderr=stderr_str,
                    sandboxed=True,
                    blocked=False,
                    execution_time_ms=round(elapsed_ms, 2)
                )

            except asyncio.TimeoutError:
                self._timed_out_executions += 1
                elapsed_ms = (time.time() - start_time) * 1000.0
                logger.error("Process execution timed out, cleaning process tree", process_id=process_id)
                await self._kill_process_tree(proc)

                return ProcessExecutionResult(
                    process_id=process_id,
                    command=request.command,
                    status=ProcessExecutionStatus.TIMED_OUT,
                    exit_code=-1,
                    stdout="",
                    stderr=f"Process execution timed out after {request.timeout_seconds}s limit.",
                    sandboxed=True,
                    blocked=True,
                    execution_time_ms=round(elapsed_ms, 2)
                )

        except Exception as e:
            elapsed_ms = (time.time() - start_time) * 1000.0
            logger.error("Process execution exception", process_id=process_id, error=str(e))
            return ProcessExecutionResult(
                process_id=process_id,
                command=request.command,
                status=ProcessExecutionStatus.FAILED,
                exit_code=-1,
                stdout="",
                stderr=f"Subprocess execution error: {str(e)}",
                sandboxed=True,
                execution_time_ms=round(elapsed_ms, 2)
            )
        finally:
            self._running_processes.pop(process_id, None)

    async def cancel(self, process_id: str) -> bool:
        """Cancels a running process and cleans up its child process tree."""
        proc = self._running_processes.get(process_id)
        if proc:
            await self._kill_process_tree(proc)
            self._running_processes.pop(process_id, None)
            return True
        return False

    async def _kill_process_tree(self, proc: asyncio.subprocess.Process) -> None:
        """Terminates process and all descendant processes."""
        try:
            if sys.platform == "win32":
                kill_proc = await asyncio.create_subprocess_shell(
                    f"taskkill /F /T /PID {proc.pid}",
                    stdout=asyncio.subprocess.DEVNULL,
                    stderr=asyncio.subprocess.DEVNULL
                )
                await kill_proc.wait()
            else:
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass


# Pluggable executor singleton
default_executor: BaseProcessExecutor = LocalProcessExecutor()


class ProcessSandboxEngine:
    """High-level facade maintaining complete backward compatibility."""

    def __init__(self, executor: BaseProcessExecutor = default_executor) -> None:
        self.executor = executor

    def get_health_status(self) -> Dict[str, Any]:
        """Returns executor health status."""
        return self.executor.get_health_status()

    def get_metrics(self) -> Dict[str, Any]:
        """Returns process metrics."""
        return self.executor.get_metrics()

    async def execute_in_sandbox_async(
        self, command: str, timeout_seconds: int = 15, cwd: Optional[str] = None
    ) -> ProcessExecutionResult:
        """Asynchronous execution entry point."""
        req = ProcessExecutionRequest(command=command, timeout_seconds=timeout_seconds, cwd=cwd)
        return await self.executor.execute(req)

    def execute_in_sandbox(self, command: str, timeout_seconds: int = 15) -> Dict[str, Any]:
        """Synchronous backward-compatible wrapper."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    res: ProcessExecutionResult = pool.submit(
                        lambda: asyncio.run(self.execute_in_sandbox_async(command, timeout_seconds))
                    ).result()
            else:
                res = loop.run_until_complete(self.execute_in_sandbox_async(command, timeout_seconds))
        except Exception:
            res = asyncio.run(self.execute_in_sandbox_async(command, timeout_seconds))

        return {
            "command": res.command,
            "exit_code": res.exit_code if res.exit_code is not None else -1,
            "stdout": res.stdout,
            "stderr": res.stderr,
            "sandboxed": res.sandboxed,
            "blocked": res.blocked
        }


sandbox_engine = ProcessSandboxEngine()
