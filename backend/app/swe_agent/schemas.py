"""
Pydantic Schemas for Enterprise Software Engineering Agent Subsystem (Sprint 8).
Defines AST nodes, patch previews, build results, test results, refactoring payloads, Git operations, and telemetry metrics.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, Field, ConfigDict


class SWEActionType(str, Enum):
    READ_REPO = "READ_REPO"
    ANALYZE_ARCH = "ANALYZE_ARCH"
    PARSE_AST = "PARSE_AST"
    MODIFY_FILE = "MODIFY_FILE"
    GENERATE_PATCH = "GENERATE_PATCH"
    APPLY_PATCH = "APPLY_PATCH"
    ROLLBACK_PATCH = "ROLLBACK_PATCH"
    RUN_BUILD = "RUN_BUILD"
    RUN_TESTS = "RUN_TESTS"
    EXECUTE_TERMINAL = "EXECUTE_TERMINAL"
    GIT_ACTION = "GIT_ACTION"
    GIT_COMMIT = "GIT_COMMIT"
    CODE_REVIEW = "CODE_REVIEW"
    REFACTOR_CODE = "REFACTOR_CODE"
    GENERATE_API = "GENERATE_API"
    DEBUG_CODE = "DEBUG_CODE"
    GENERATE_DOCS = "GENERATE_DOCS"
    ANALYZE_DEPENDENCIES = "ANALYZE_DEPENDENCIES"
    STATIC_ANALYSIS = "STATIC_ANALYSIS"
    VERIFY_PIPELINE = "VERIFY_PIPELINE"
    RESTORE_BACKUP = "RESTORE_BACKUP"


class ASTNodeInfo(BaseModel):
    """Platform-agnostic AST Node Descriptor."""
    node_type: str = Field(..., description="ClassDef, FunctionDef, Import, Interface, Export, etc.")
    name: str = Field(..., description="Symbol or declaration name")
    line_number: int = 1
    end_line_number: Optional[int] = None
    docstring: Optional[str] = None
    parameters: List[str] = Field(default_factory=list)
    children_count: int = 0


class ASTParseResult(BaseModel):
    """AST Parsing Result payload."""
    file_path: str
    language: str
    nodes: List[ASTNodeInfo] = Field(default_factory=list)
    syntax_valid: bool = True
    error_message: Optional[str] = None


class PatchPreview(BaseModel):
    """Unified Diff Patch Descriptor."""
    patch_id: str = Field(default_factory=lambda: f"patch-{uuid.uuid4().hex[:8]}")
    file_path: str
    unified_diff: str
    additions: int = 0
    deletions: int = 0
    has_conflicts: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)


class BuildResult(BaseModel):
    """Build execution outcome descriptor."""
    build_system: str  # maven, gradle, npm, pip, cargo, go, dotnet
    success: bool
    exit_code: int = 0
    duration_seconds: float = 0.0
    stdout: str = ""
    stderr: str = ""
    artifacts: List[str] = Field(default_factory=list)


class TestResultDetails(BaseModel):
    """Test suite execution outcome descriptor."""
    test_framework: str  # pytest, jest, junit, cargo_test
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    skipped_tests: int = 0
    duration_seconds: float = 0.0
    success: bool = True
    coverage_percent: Optional[float] = None
    failure_messages: List[str] = Field(default_factory=list)


class FileBackupInfo(BaseModel):
    """Metadata payload for pre-edit file backups."""
    backup_id: str = Field(default_factory=lambda: f"bak-{uuid.uuid4().hex[:8]}")
    original_path: str
    backup_path: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    checksum: str = Field(..., description="SHA256 checksum of original content")


class CodeModificationLog(BaseModel):
    """Modification audit log entry."""
    log_id: str = Field(default_factory=lambda: f"mod-{uuid.uuid4().hex[:8]}")
    file_path: str
    action_type: str
    diff_summary: str
    backup_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class CodeReviewIssue(BaseModel):
    """Specific code review issue finding."""
    line_number: int = 1
    severity: str = "INFO"  # INFO, WARNING, CRITICAL
    category: str = "SOLID_PRINCIPLE"  # SOLID, CLEAN_ARCH, PERFORMANCE, SECURITY
    message: str
    suggestion: str


class CodeReviewResult(BaseModel):
    """Result payload for automated code review."""
    file_path: str
    quality_score: float = Field(default=8.5, ge=0.0, le=10.0)
    issues: List[CodeReviewIssue] = Field(default_factory=list)
    summary: str


class DependencyAnalysisResult(BaseModel):
    """Dependency analysis payload."""
    direct_dependencies: List[str]
    transitive_count: int
    vulnerabilities_found: int = 0
    tree_json: Dict[str, Any] = Field(default_factory=dict)


class StaticAnalysisResult(BaseModel):
    """Static analysis linting and complexity payload."""
    lint_errors: List[Dict[str, Any]] = Field(default_factory=list)
    cyclomatic_complexity: int = 3
    security_warnings: List[str] = Field(default_factory=list)
    passed: bool = True


class VerificationPipelineResult(BaseModel):
    """Structured result of 5-stage verification pipeline."""
    pipeline_id: str = Field(default_factory=lambda: f"ver-{uuid.uuid4().hex[:8]}")
    patch_applied: bool = True
    build_passed: bool = True
    tests_passed: bool = True
    static_analysis_passed: bool = True
    code_review_passed: bool = True
    overall_success: bool = True
    rolled_back: bool = False
    details: Dict[str, Any] = Field(default_factory=dict)


class SWERequest(BaseModel):
    """Request payload for Software Engineering Agent action."""
    action_type: SWEActionType
    repo_path: Optional[str] = Field(default=".", description="Repository target directory")
    file_path: Optional[str] = Field(default=None, description="Target file path")
    content: Optional[str] = Field(default=None, description="File code content or patch content")
    command: Optional[str] = Field(default=None, description="Terminal command line string")
    prompt: Optional[str] = Field(default=None, description="Natural language instructions for code gen/debug/docs")
    commit_message: Optional[str] = Field(default=None, description="Git commit message")
    git_command: Optional[str] = Field(default=None, description="Git command subcommand (status, diff, branch, checkout, stash, tag)")
    build_system: Optional[str] = Field(default=None, description="Target build system (maven, gradle, npm, pip, cargo)")
    backup_id: Optional[str] = Field(default=None, description="Backup ID for restoration")
    parameters: Dict[str, Any] = Field(default_factory=dict)


class SWEResponse(BaseModel):
    """Response payload for Software Engineering Agent action."""
    model_config = ConfigDict(from_attributes=True)

    action_id: str = Field(default_factory=lambda: f"swe-{uuid.uuid4().hex[:8]}")
    action_type: SWEActionType
    status: str = "SUCCESS"  # SUCCESS, FAILED, RESTORED, ROLLED_BACK
    result: Optional[Any] = None
    error_message: Optional[str] = None
    backup_created: bool = False
    backup_info: Optional[FileBackupInfo] = None
    modification_log: Optional[CodeModificationLog] = None
    executed_at: datetime = Field(default_factory=datetime.utcnow)
