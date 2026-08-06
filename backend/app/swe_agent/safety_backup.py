"""
File Backup and Modification Audit Logger Engine.
Enforces mandatory backup creation before file overwrites and logs every modification.
"""

import hashlib

import json
import os
import shutil
from datetime import datetime
from typing import Dict, List, Optional
from app.swe_agent.schemas import CodeModificationLog, FileBackupInfo


class SafetyBackupEngine:
    """Manages pre-edit backups and modification audit logging."""

    def __init__(self, backup_dir: str = ".swe_backups") -> None:
        self.backup_dir = os.path.abspath(backup_dir)
        self.log_file = os.path.join(self.backup_dir, "modification_log.json")
        self._backup_registry: Dict[str, FileBackupInfo] = {}
        os.makedirs(self.backup_dir, exist_ok=True)
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w", encoding="utf-8") as f:
                json.dump([], f)

    def create_pre_edit_backup(self, file_path: str) -> Optional[FileBackupInfo]:
        """
        MANDATORY RULE 1: Creates a timestamped backup snapshot before any existing file overwrite.
        """
        abs_path = os.path.abspath(file_path)
        if not os.path.exists(abs_path) or os.path.isdir(abs_path):
            return None

        with open(abs_path, "rb") as f:
            content_bytes = f.read()

        checksum = hashlib.sha256(content_bytes).hexdigest()
        filename = os.path.basename(abs_path)
        timestamp_str = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
        backup_filename = f"{filename}.{timestamp_str}.bak"
        backup_abs_path = os.path.join(self.backup_dir, backup_filename)

        shutil.copy2(abs_path, backup_abs_path)

        info = FileBackupInfo(
            original_path=abs_path,
            backup_path=backup_abs_path,
            checksum=checksum
        )
        self._backup_registry[info.backup_id] = info
        return info

    def log_modification(
        self,
        file_path: str,
        action_type: str,
        diff_summary: str,
        backup_id: Optional[str] = None
    ) -> CodeModificationLog:
        """
        MANDATORY RULE 2: Logs every modification into modification_log.json audit log.
        """
        log_entry = CodeModificationLog(
            file_path=os.path.abspath(file_path),
            action_type=action_type,
            diff_summary=diff_summary,
            backup_id=backup_id
        )

        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                logs = json.load(f)
        except Exception:
            logs = []

        logs.append(log_entry.model_dump(mode="json"))

        with open(self.log_file, "w", encoding="utf-8") as f:
            json.dump(logs, f, indent=2)

        return log_entry

    def list_modification_logs(self) -> List[CodeModificationLog]:
        """Lists modification audit trail records."""
        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                logs = json.load(f)
            return [CodeModificationLog.model_validate(l) for l in logs]
        except Exception:
            return []

    def restore_backup(self, backup_id: str) -> bool:
        """Restores file from backup snapshot."""
        info = self._backup_registry.get(backup_id)
        if info and os.path.exists(info.backup_path):
            shutil.copy2(info.backup_path, info.original_path)
            return True
        return False



safety_backup_engine = SafetyBackupEngine()
