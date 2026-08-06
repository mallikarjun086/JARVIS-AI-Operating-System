"""
Multi-Language AST Parsing Engine (Sprint 8 Step 4).
Provides language-aware AST parsing for Python, JavaScript/TypeScript, Java, JSON, YAML, Markdown, and XML.
Allows SWE Agent to reason over AST nodes rather than raw text strings.
"""

import ast
import json
import os
import re
from typing import List, Optional
import structlog

from app.swe_agent.schemas import ASTNodeInfo, ASTParseResult

logger = structlog.get_logger(__name__)


class ASTEngine:
    """Multi-language AST Parser."""

    @classmethod
    def parse_file(cls, file_path: str) -> ASTParseResult:
        """Parses source code file into a structured ASTParseResult."""
        if not os.path.exists(file_path):
            return ASTParseResult(
                file_path=file_path,
                language="unknown",
                syntax_valid=False,
                error_message=f"File not found: {file_path}"
            )

        ext = os.path.splitext(file_path)[1].lower()
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            return ASTParseResult(
                file_path=file_path,
                language="unknown",
                syntax_valid=False,
                error_message=str(e)
            )

        if ext in [".py"]:
            return cls._parse_python(file_path, content)
        elif ext in [".js", ".jsx", ".ts", ".tsx"]:
            return cls._parse_javascript_typescript(file_path, content, ext)
        elif ext in [".java"]:
            return cls._parse_java(file_path, content)
        elif ext in [".json"]:
            return cls._parse_json(file_path, content)
        elif ext in [".yaml", ".yml"]:
            return cls._parse_yaml(file_path, content)
        elif ext in [".md", ".markdown"]:
            return cls._parse_markdown(file_path, content)
        elif ext in [".xml", ".html"]:
            return cls._parse_xml(file_path, content)
        else:
            return ASTParseResult(
                file_path=file_path,
                language="text",
                syntax_valid=True,
                nodes=[ASTNodeInfo(node_type="TextFile", name=os.path.basename(file_path), line_number=1)]
            )

    @classmethod
    def _parse_python(cls, file_path: str, content: str) -> ASTParseResult:
        """Parses Python code using stdlib ast module."""
        try:
            tree = ast.parse(content, filename=file_path)
            nodes = []

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    nodes.append(
                        ASTNodeInfo(
                            node_type="ClassDef",
                            name=node.name,
                            line_number=node.lineno,
                            docstring=ast.get_docstring(node),
                            children_count=len(node.body)
                        )
                    )
                elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                    params = [arg.arg for arg in node.args.args]
                    is_async = isinstance(node, ast.AsyncFunctionDef)
                    nodes.append(
                        ASTNodeInfo(
                            node_type="AsyncFunctionDef" if is_async else "FunctionDef",
                            name=node.name,
                            line_number=node.lineno,
                            parameters=params,
                            docstring=ast.get_docstring(node),
                            children_count=len(node.body)
                        )
                    )
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    mod_name = getattr(node, "module", None) or "import"
                    nodes.append(ASTNodeInfo(node_type="Import", name=mod_name, line_number=node.lineno))

            return ASTParseResult(file_path=file_path, language="python", syntax_valid=True, nodes=nodes)

        except SyntaxError as se:
            return ASTParseResult(
                file_path=file_path,
                language="python",
                syntax_valid=False,
                error_message=f"SyntaxError at line {se.lineno}: {se.msg}"
            )

    @classmethod
    def _parse_javascript_typescript(cls, file_path: str, content: str, ext: str) -> ASTParseResult:
        """Parses JS/TS files using regex tokenization for Classes, Functions, and Imports."""
        nodes = []
        lines = content.split("\n")

        for idx, line in enumerate(lines, 1):
            # Class match
            cls_m = re.search(r"class\s+([A-Za-z0-9_]+)", line)
            if cls_m:
                nodes.append(ASTNodeInfo(node_type="ClassDef", name=cls_m.group(1), line_number=idx))

            # Function / Arrow Function match
            fn_m = re.search(r"(?:function\s+([A-Za-z0-9_]+)|const\s+([A-Za-z0-9_]+)\s*=\s*(?:async\s*)?\()", line)
            if fn_m:
                fn_name = fn_m.group(1) or fn_m.group(2)
                nodes.append(ASTNodeInfo(node_type="FunctionDef", name=fn_name, line_number=idx))

            # Import match
            imp_m = re.search(r"import\s+.*?from\s+[\"'](.*?)[\"']", line)
            if imp_m:
                nodes.append(ASTNodeInfo(node_type="Import", name=imp_m.group(1), line_number=idx))

        return ASTParseResult(file_path=file_path, language="typescript" if "ts" in ext else "javascript", syntax_valid=True, nodes=nodes)

    @classmethod
    def _parse_java(cls, file_path: str, content: str) -> ASTParseResult:
        """Parses Java files using regex tokenization for Classes, Interfaces, and Methods."""
        nodes = []
        lines = content.split("\n")

        for idx, line in enumerate(lines, 1):
            cls_m = re.search(r"(?:public|private|protected)?\s*(?:class|interface|enum)\s+([A-Za-z0-9_]+)", line)
            if cls_m:
                nodes.append(ASTNodeInfo(node_type="ClassDef", name=cls_m.group(1), line_number=idx))

            mth_m = re.search(r"(?:public|private|protected)\s+(?:static\s+)?[A-Za-z0-9_<>]+\s+([A-Za-z0-9_]+)\s*\(", line)
            if mth_m:
                nodes.append(ASTNodeInfo(node_type="MethodDef", name=mth_m.group(1), line_number=idx))

        return ASTParseResult(file_path=file_path, language="java", syntax_valid=True, nodes=nodes)

    @classmethod
    def _parse_json(cls, file_path: str, content: str) -> ASTParseResult:
        """Parses JSON files."""
        try:
            parsed = json.loads(content)
            keys = list(parsed.keys()) if isinstance(parsed, dict) else [f"array_len_{len(parsed)}"]
            nodes = [ASTNodeInfo(node_type="JsonObject", name=k, line_number=1) for k in keys]
            return ASTParseResult(file_path=file_path, language="json", syntax_valid=True, nodes=nodes)
        except Exception as e:
            return ASTParseResult(file_path=file_path, language="json", syntax_valid=False, error_message=str(e))

    @classmethod
    def _parse_yaml(cls, file_path: str, content: str) -> ASTParseResult:
        """Parses YAML configuration files."""
        lines = content.split("\n")
        nodes = []
        for idx, line in enumerate(lines, 1):
            if ":" in line and not line.strip().startswith("#"):
                key = line.split(":")[0].strip()
                if key:
                    nodes.append(ASTNodeInfo(node_type="YamlKey", name=key, line_number=idx))
        return ASTParseResult(file_path=file_path, language="yaml", syntax_valid=True, nodes=nodes)

    @classmethod
    def _parse_markdown(cls, file_path: str, content: str) -> ASTParseResult:
        """Parses Markdown headings."""
        nodes = []
        lines = content.split("\n")
        for idx, line in enumerate(lines, 1):
            if line.startswith("#"):
                heading = line.lstrip("#").strip()
                nodes.append(ASTNodeInfo(node_type="Heading", name=heading, line_number=idx))
        return ASTParseResult(file_path=file_path, language="markdown", syntax_valid=True, nodes=nodes)

    @classmethod
    def _parse_xml(cls, file_path: str, content: str) -> ASTParseResult:
        """Parses XML/HTML elements."""
        tags = re.findall(r"<([A-Za-z0-9_\-]+)[^>]*>", content)
        nodes = [ASTNodeInfo(node_type="XmlElement", name=t, line_number=1) for t in set(tags[:20])]
        return ASTParseResult(file_path=file_path, language="xml", syntax_valid=True, nodes=nodes)


ast_engine = ASTEngine()
