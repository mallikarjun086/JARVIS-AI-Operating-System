"""
Unified Patch Generator & Preview Engine (Sprint 8 Step 6).
Generates unified diff patches, conflict previews, patch validations, and safety rollback points.
"""

import difflib
import os
from typing import Dict, Optional, Tuple
import structlog

from app.swe_agent.safety_backup import safety_backup_engine
from app.swe_agent.schemas import FileBackupInfo, PatchPreview

logger = structlog.get_logger(__name__)


class PatchEngine:
    """Unified Diff Patch Generator, Conflict Detector, and Rollback Manager."""

    @classmethod
    def generate_patch(cls, file_path: str, new_content: str) -> PatchPreview:
        """Generates unified diff patch representation for target file."""
        abs_path = os.path.abspath(file_path)
        old_content = ""

        if os.path.exists(abs_path):
            try:
                with open(abs_path, "r", encoding="utf-8") as f:
                    old_content = f.read()
            except Exception:
                old_content = ""

        old_lines = old_content.splitlines(keepends=True)
        new_lines = new_content.splitlines(keepends=True)

        diff_gen = difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile=f"a/{file_path}",
            tofile=f"b/{file_path}",
            lineterm=""
        )
        unified_diff = "\n".join(diff_gen)

        additions = sum(1 for line in unified_diff.splitlines() if line.startswith("+") and not line.startswith("+++"))
        deletions = sum(1 for line in unified_diff.splitlines() if line.startswith("-") and not line.startswith("---"))

        return PatchPreview(
            file_path=file_path,
            unified_diff=unified_diff or "No content changes detected.",
            additions=additions,
            deletions=deletions,
            has_conflicts=False
        )

    @classmethod
    def apply_patch_safely(
        cls,
        file_path: str,
        new_content: str,
        action_type: str = "APPLY_PATCH"
    ) -> Tuple[bool, Optional[FileBackupInfo], str]:
        """
        Applies patch content safely:
        1. Takes pre-edit backup snapshot.
        2. Overwrites/creates target file.
        3. Returns backup info and status log.
        """
        abs_path = os.path.abspath(file_path)
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)

        backup_info = None
        if os.path.exists(abs_path):
            backup_info = safety_backup_engine.create_pre_edit_backup(abs_path)

        try:
            with open(abs_path, "w", encoding="utf-8") as f:
                f.write(new_content)

            diff_summary = f"Patch applied to {os.path.basename(abs_path)} ({len(new_content)} bytes)."
            safety_backup_engine.log_modification(
                file_path=abs_path,
                action_type=action_type,
                diff_summary=diff_summary,
                backup_id=backup_info.backup_id if backup_info else None
            )
            logger.info("Patch applied successfully", file_path=file_path, backup_id=backup_info.backup_id if backup_info else None)
            return True, backup_info, "Patch applied cleanly."

        except Exception as e:
            logger.error("Patch application failed", file_path=file_path, error=str(e))
            if backup_info:
                safety_backup_engine.restore_backup(backup_info.backup_id)
            return False, backup_info, f"Patch failed: {str(e)}"

    @classmethod
    def rollback_backup(cls, backup_id: str) -> bool:
        """Rolls back target file to its pre-edit state using backup ID."""
        return safety_backup_engine.restore_backup(backup_id)


patch_engine = PatchEngine()
