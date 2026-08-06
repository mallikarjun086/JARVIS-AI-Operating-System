"""
Software Engineering Agent Manager (Sprint 8).
Orchestrates autonomous software engineering workflows enforcing mandatory safety backup rules and verification pipelines.
"""

from app.swe_agent.analyzer import analyzer_engine
from app.swe_agent.ast_engine import ast_engine
from app.swe_agent.build_manager import build_manager
from app.swe_agent.git_manager import git_manager
from app.swe_agent.patch_engine import patch_engine
from app.swe_agent.repo_engine import repo_engine
from app.swe_agent.safety_backup import safety_backup_engine
from app.swe_agent.schemas import SWEActionType, SWERequest, SWEResponse
from app.swe_agent.test_manager import test_manager
from app.swe_agent.verification_pipeline import verification_pipeline


class SoftwareEngineeringAgent:
    """Autonomous Software Engineering Agent orchestrator."""

    @classmethod
    async def execute_action(cls, req: SWERequest) -> SWEResponse:
        """Executes software engineering action adhering to mandatory safety backup rules and verification pipeline."""
        resp = SWEResponse(action_type=req.action_type, status="SUCCESS")

        if req.action_type == SWEActionType.READ_REPO:
            resp.result = repo_engine.read_repository(req.repo_path or ".")

        elif req.action_type == SWEActionType.ANALYZE_ARCH:
            resp.result = analyzer_engine.analyze_architecture(req.repo_path or ".")

        elif req.action_type == SWEActionType.PARSE_AST:
            if not req.file_path:
                return SWEResponse(action_type=req.action_type, status="FAILED", error_message="file_path required for AST parsing.")
            resp.result = ast_engine.parse_file(req.file_path).model_dump()

        elif req.action_type == SWEActionType.GENERATE_PATCH:
            if not req.file_path or req.content is None:
                return SWEResponse(action_type=req.action_type, status="FAILED", error_message="file_path and content required for patch generation.")
            resp.result = patch_engine.generate_patch(req.file_path, req.content).model_dump()

        elif req.action_type == SWEActionType.APPLY_PATCH or req.action_type == SWEActionType.MODIFY_FILE:
            if not req.file_path or req.content is None:
                return SWEResponse(action_type=req.action_type, status="FAILED", error_message="file_path and content required.")

            applied, backup_info, log_msg = patch_engine.apply_patch_safely(
                file_path=req.file_path,
                new_content=req.content,
                action_type=req.action_type.value
            )
            resp.backup_created = backup_info is not None
            resp.backup_info = backup_info
            resp.status = "SUCCESS" if applied else "FAILED"
            resp.result = {"applied": applied, "message": log_msg, "file_path": req.file_path}

        elif req.action_type == SWEActionType.ROLLBACK_PATCH:
            if not req.backup_id:
                return SWEResponse(action_type=req.action_type, status="FAILED", error_message="backup_id required for rollback.")
            restored = patch_engine.rollback_backup(req.backup_id)
            resp.status = "RESTORED" if restored else "FAILED"
            resp.result = {"restored": restored, "backup_id": req.backup_id}

        elif req.action_type == SWEActionType.RUN_BUILD:
            resp.result = build_manager.execute_build(build_system=req.build_system, repo_path=req.repo_path or ".").model_dump()

        elif req.action_type == SWEActionType.RUN_TESTS:
            resp.result = test_manager.run_test_suite(command=req.command, repo_path=req.repo_path or ".").model_dump()

        elif req.action_type == SWEActionType.EXECUTE_TERMINAL:
            resp.result = repo_engine.execute_terminal(req.command or "echo TERMINAL")

        elif req.action_type == SWEActionType.GIT_ACTION or req.action_type == SWEActionType.GIT_COMMIT:
            cmd = req.git_command or "status"
            if cmd == "commit":
                resp.result = git_manager.commit_changes(req.commit_message or "chore: SWE Agent automated commit", repo_path=req.repo_path or ".")
            elif cmd == "diff":
                resp.result = {"diff": git_manager.get_diff(file_path=req.file_path, repo_path=req.repo_path or ".")}
            elif cmd == "branch":
                resp.result = git_manager.list_branches(repo_path=req.repo_path or ".")
            elif cmd == "stash":
                resp.result = git_manager.stash(repo_path=req.repo_path or ".")
            else:
                resp.result = git_manager.get_status(repo_path=req.repo_path or ".")

        elif req.action_type == SWEActionType.CODE_REVIEW:
            resp.result = (await analyzer_engine.perform_code_review(req.file_path or "backend/app/main.py")).model_dump()

        elif req.action_type == SWEActionType.REFACTOR_CODE:
            resp.result = analyzer_engine.refactor_code(req.file_path or "backend/app/main.py", req.parameters.get("refactor_type", "DEAD_CODE_REMOVAL"))

        elif req.action_type == SWEActionType.GENERATE_API:
            resp.result = await analyzer_engine.generate_api(req.prompt or "orders", ["id", "amount", "status"])

        elif req.action_type == SWEActionType.DEBUG_CODE:
            resp.result = await analyzer_engine.debug_code(req.prompt or "ImportError: module not found")

        elif req.action_type == SWEActionType.GENERATE_DOCS:
            resp.result = await analyzer_engine.generate_docs(req.file_path or "backend/app/main.py")

        elif req.action_type == SWEActionType.ANALYZE_DEPENDENCIES:
            resp.result = analyzer_engine.analyze_dependencies(req.file_path or "requirements.txt").model_dump()

        elif req.action_type == SWEActionType.STATIC_ANALYSIS:
            resp.result = analyzer_engine.perform_static_analysis(req.file_path or "backend/app/main.py").model_dump()

        elif req.action_type == SWEActionType.VERIFY_PIPELINE:
            if not req.file_path or req.content is None:
                return SWEResponse(action_type=req.action_type, status="FAILED", error_message="file_path and content required for verification pipeline.")

            pipe_res = await verification_pipeline.verify_and_apply_patch(
                file_path=req.file_path,
                new_content=req.content,
                build_system=req.build_system,
                test_command=req.command,
                repo_path=req.repo_path or "."
            )
            resp.status = "SUCCESS" if pipe_res.overall_success else "ROLLED_BACK"
            resp.result = pipe_res.model_dump()

        elif req.action_type == SWEActionType.RESTORE_BACKUP:
            if not req.backup_id:
                return SWEResponse(action_type=req.action_type, status="FAILED", error_message="backup_id required.")
            restored = safety_backup_engine.restore_backup(req.backup_id)
            resp.status = "RESTORED" if restored else "FAILED"
            resp.result = {"restored": restored, "backup_id": req.backup_id}

        return resp


swe_agent = SoftwareEngineeringAgent()
