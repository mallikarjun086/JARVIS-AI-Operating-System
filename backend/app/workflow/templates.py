"""
Pre-Built Enterprise Workflow Templates (Sprint 10 Step 9).
Provides 8 reusable enterprise templates:
1. Automated Internship Application Pipeline
2. Automated Repository Analysis & Health Audit
3. Spring Boot Microservice Generation Pipeline
4. Documentation Generation & Synthesis Pipeline
5. Enterprise Deployment Pipeline
6. Automated Code Review & Refactoring Pipeline
7. Automated Bug Fixing & Verification Pipeline
8. Autonomous Deep Research Pipeline
"""

from typing import List
from app.workflow.schemas import NodeType, WorkflowDefinition, WorkflowNode


def get_all_enterprise_templates() -> List[WorkflowDefinition]:
    """Returns list of all 8 pre-built enterprise workflow templates."""
    return [
        get_internship_workflow_template(),
        get_repo_analysis_template(),
        get_spring_boot_generation_template(),
        get_docs_generation_template(),
        get_deployment_pipeline_template(),
        get_code_review_refactor_template(),
        get_bug_fixing_template(),
        get_deep_research_template()
    ]


def get_internship_workflow_template() -> WorkflowDefinition:
    """1. Internship Application Pipeline."""
    nodes = [
        WorkflowNode(node_id="node_1", node_type=NodeType.ACTION, plugin_name="BrowserNode", name="Find Internships", action_name="find_internships", next_nodes=["node_2"]),
        WorkflowNode(node_id="node_2", node_type=NodeType.ACTION, plugin_name="SWENode", name="Tailor Resume", action_name="tailor_resume", next_nodes=["node_3"]),
        WorkflowNode(node_id="node_3", node_type=NodeType.ACTION, plugin_name="SWENode", name="Generate Cover Letter", action_name="generate_cover_letter", next_nodes=["node_4"]),
        WorkflowNode(node_id="node_4", node_type=NodeType.HUMAN_APPROVAL, plugin_name="ApprovalNode", name="Review Application Package", action_name="request_human_approval", next_nodes=["node_5"]),
        WorkflowNode(node_id="node_5", node_type=NodeType.ACTION, plugin_name="BrowserNode", name="Submit Application", action_name="submit_application", next_nodes=["node_6"]),
        WorkflowNode(node_id="node_6", node_type=NodeType.ACTION, plugin_name="BrowserNode", name="Track Status", action_name="track_status", next_nodes=["node_7"]),
        WorkflowNode(node_id="node_7", node_type=NodeType.ACTION, plugin_name="DesktopNode", name="Update Spreadsheet", action_name="update_spreadsheet", next_nodes=["node_8"]),
        WorkflowNode(node_id="node_8", node_type=NodeType.ACTION, plugin_name="SlackNode", name="Notify User", action_name="notify_user", next_nodes=[])
    ]
    return WorkflowDefinition(definition_id="tmpl-internship", name="Automated Internship Application Pipeline", description="Finds internships, tailors resume, generates cover letter, pauses for human approval, submits application, tracks status, updates spreadsheet, and notifies user.", nodes=nodes)


def get_repo_analysis_template() -> WorkflowDefinition:
    """2. Automated Repository Analysis & Health Audit."""
    nodes = [
        WorkflowNode(node_id="node_1", node_type=NodeType.ACTION, plugin_name="GitNode", name="Clone Repository", action_name="clone_repo", next_nodes=["node_2"]),
        WorkflowNode(node_id="node_2", node_type=NodeType.ACTION, plugin_name="SWENode", name="Parse AST Structure", action_name="parse_ast", next_nodes=["node_3"]),
        WorkflowNode(node_id="node_3", node_type=NodeType.ACTION, plugin_name="SWENode", name="Static Analysis & Linting", action_name="static_analysis", next_nodes=["node_4"]),
        WorkflowNode(node_id="node_4", node_type=NodeType.ACTION, plugin_name="SWENode", name="Generate Architecture Audit Report", action_name="generate_report", next_nodes=[])
    ]
    return WorkflowDefinition(definition_id="tmpl-repo-analysis", name="Automated Repository Analysis & Health Audit", description="Analyzes repo structure, AST nodes, cyclomatic complexity, and architecture health.", nodes=nodes)


def get_spring_boot_generation_template() -> WorkflowDefinition:
    """3. Spring Boot Microservice Generation Pipeline."""
    nodes = [
        WorkflowNode(node_id="node_1", node_type=NodeType.ACTION, plugin_name="SWENode", name="Generate JPA Entities & Schemas", action_name="gen_entities", next_nodes=["node_2"]),
        WorkflowNode(node_id="node_2", node_type=NodeType.ACTION, plugin_name="SWENode", name="Generate REST Controllers & Repositories", action_name="gen_controllers", next_nodes=["node_3"]),
        WorkflowNode(node_id="node_3", node_type=NodeType.ACTION, plugin_name="DockerNode", name="Execute Maven Build & Tests", action_name="maven_build", next_nodes=[])
    ]
    return WorkflowDefinition(definition_id="tmpl-spring-boot", name="Spring Boot Microservice Generation Pipeline", description="Generates Java Spring Boot microservice scaffolding with maven build verification.", nodes=nodes)


def get_docs_generation_template() -> WorkflowDefinition:
    """4. Documentation Generation & Synthesis Pipeline."""
    nodes = [
        WorkflowNode(node_id="node_1", node_type=NodeType.ACTION, plugin_name="SWENode", name="Extract API Signatures", action_name="extract_signatures", next_nodes=["node_2"]),
        WorkflowNode(node_id="node_2", node_type=NodeType.ACTION, plugin_name="SWENode", name="Generate Markdown Documentation", action_name="generate_markdown", next_nodes=[])
    ]
    return WorkflowDefinition(definition_id="tmpl-docs-gen", name="Documentation Generation & Synthesis Pipeline", description="Extracts API definitions and generates comprehensive technical markdown docs.", nodes=nodes)


def get_deployment_pipeline_template() -> WorkflowDefinition:
    """5. Enterprise Deployment Pipeline."""
    nodes = [
        WorkflowNode(node_id="node_1", node_type=NodeType.ACTION, plugin_name="DockerNode", name="Build Container Image", action_name="build_image", next_nodes=["node_2"]),
        WorkflowNode(node_id="node_2", node_type=NodeType.HUMAN_APPROVAL, plugin_name="ApprovalNode", name="Approve Staging Deployment", action_name="approve_deploy", next_nodes=["node_3"]),
        WorkflowNode(node_id="node_3", node_type=NodeType.ACTION, plugin_name="DockerNode", name="Deploy Microservice Container", action_name="deploy_container", next_nodes=[])
    ]
    return WorkflowDefinition(definition_id="tmpl-deploy", name="Enterprise Deployment Pipeline", description="Builds Docker container image and deploys with staging approval gate.", nodes=nodes)


def get_code_review_refactor_template() -> WorkflowDefinition:
    """6. Automated Code Review & Refactoring Pipeline."""
    nodes = [
        WorkflowNode(node_id="node_1", node_type=NodeType.ACTION, plugin_name="SWENode", name="SOLID Principles Code Review", action_name="solid_review", next_nodes=["node_2"]),
        WorkflowNode(node_id="node_2", node_type=NodeType.ACTION, plugin_name="SWENode", name="Execute Dead Code Removal Refactoring", action_name="refactor_dead_code", next_nodes=[])
    ]
    return WorkflowDefinition(definition_id="tmpl-code-review", name="Automated Code Review & Refactoring Pipeline", description="Performs SOLID principles code review and applies clean refactorings.", nodes=nodes)


def get_bug_fixing_template() -> WorkflowDefinition:
    """7. Automated Bug Fixing & Verification Pipeline."""
    nodes = [
        WorkflowNode(node_id="node_1", node_type=NodeType.ACTION, plugin_name="SWENode", name="Reproduce Test Failure", action_name="run_failing_test", next_nodes=["node_2"]),
        WorkflowNode(node_id="node_2", node_type=NodeType.ACTION, plugin_name="SWENode", name="Generate Unified Diff Patch", action_name="gen_patch", next_nodes=["node_3"]),
        WorkflowNode(node_id="node_3", node_type=NodeType.ACTION, plugin_name="SWENode", name="Verify 5-Stage Verification Pipeline", action_name="verify_pipeline", next_nodes=[])
    ]
    return WorkflowDefinition(definition_id="tmpl-bug-fix", name="Automated Bug Fixing & Verification Pipeline", description="Reproduces test failures, generates patches, and verifies via 5-stage verification.", nodes=nodes)


def get_deep_research_template() -> WorkflowDefinition:
    """8. Autonomous Deep Research Pipeline."""
    nodes = [
        WorkflowNode(node_id="node_1", node_type=NodeType.ACTION, plugin_name="BrowserNode", name="Search Academic & Tech Specs", action_name="web_search", next_nodes=["node_2"]),
        WorkflowNode(node_id="node_2", node_type=NodeType.ACTION, plugin_name="SWENode", name="Synthesize Research Executive Summary", action_name="synthesize_summary", next_nodes=[])
    ]
    return WorkflowDefinition(definition_id="tmpl-research", name="Autonomous Deep Research Pipeline", description="Performs multi-source web research and synthesizes structured summaries.", nodes=nodes)
