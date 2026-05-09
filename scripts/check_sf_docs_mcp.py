#!/usr/bin/env python3
"""
Validate the project-local Salesforce docs MCP configuration.

Read-only: no clone, build, or network calls. Validates the committed
`.mcp.json` `sf-docs` entry, the launcher wrapper, and local runtime
preconditions (node, the server entry file). Missing runtime preconditions
are WARN, not FAIL — they are expected before a project finishes installing
the upstream sf-docs-mcp clone.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


SF_DOCS_SERVER_KEY = "sf-docs"
EXPECTED_COMMAND = "bash"
EXPECTED_ARGS = ["scripts/launch_sf_docs_mcp.sh"]
WRAPPER_RELATIVE_PATH = Path("scripts/launch_sf_docs_mcp.sh")
DEFAULT_SERVER_PATH = Path.home() / ".sf-docs-mcp" / "dist" / "mcp-server.js"


@dataclass
class CheckResult:
    name: str
    status: str
    detail: str
    manual_step: str | None = None


def determine_overall_status(checks: list[CheckResult]) -> str:
    statuses = [check.status for check in checks]
    if "ERROR" in statuses:
        return "ERROR"
    if "FAIL" in statuses:
        return "FAIL"
    if "WARN" in statuses:
        return "WARN"
    return "PASS"


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise RuntimeError(f"MCP config does not exist: {path}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Could not parse JSON from {path}") from exc


def check_config_entry(config_path: Path, checks: list[CheckResult]) -> bool:
    if not config_path.exists():
        checks.append(
            CheckResult(
                name="Project MCP config file",
                status="FAIL",
                detail=f"Project MCP config is missing: `{config_path}`.",
                manual_step="Restore the committed `.mcp.json` file before relying on sf-docs MCP.",
            )
        )
        return False

    checks.append(
        CheckResult(
            name="Project MCP config file",
            status="PASS",
            detail=f"Found project MCP config at `{config_path}`.",
        )
    )

    try:
        config = read_json(config_path)
    except RuntimeError as exc:
        checks.append(CheckResult(name="Project MCP config JSON", status="ERROR", detail=str(exc)))
        return False

    mcp_servers = config.get("mcpServers")
    if not isinstance(mcp_servers, dict):
        checks.append(
            CheckResult(
                name="MCP servers object",
                status="FAIL",
                detail="`mcpServers` is missing or not an object in `.mcp.json`.",
                manual_step="Restore the Boilerplate MCP structure before using sf-docs MCP.",
            )
        )
        return False

    server = mcp_servers.get(SF_DOCS_SERVER_KEY)
    if not isinstance(server, dict):
        checks.append(
            CheckResult(
                name="sf-docs server entry",
                status="FAIL",
                detail="No `sf-docs` server entry is configured in `.mcp.json`.",
                manual_step="Restore the committed sf-docs MCP entry before relying on sf-docs MCP.",
            )
        )
        return False

    command = server.get("command")
    args = server.get("args")
    if command == EXPECTED_COMMAND and isinstance(args, list) and [str(a) for a in args] == EXPECTED_ARGS:
        checks.append(
            CheckResult(
                name="sf-docs launch command",
                status="PASS",
                detail="Configured for `bash scripts/launch_sf_docs_mcp.sh`.",
            )
        )
    else:
        checks.append(
            CheckResult(
                name="sf-docs launch command",
                status="FAIL",
                detail="sf-docs entry does not match the expected `bash scripts/launch_sf_docs_mcp.sh` form.",
                manual_step="Restore the Boilerplate sf-docs server definition in `.mcp.json`.",
            )
        )

    return True


def check_wrapper(repo_root: Path, checks: list[CheckResult]) -> None:
    wrapper = repo_root / WRAPPER_RELATIVE_PATH
    if not wrapper.exists():
        checks.append(
            CheckResult(
                name="Launcher wrapper",
                status="FAIL",
                detail=f"Wrapper script missing at `{WRAPPER_RELATIVE_PATH}`.",
                manual_step="Restore `scripts/launch_sf_docs_mcp.sh` from Boilerplate.",
            )
        )
        return

    if not os.access(wrapper, os.X_OK):
        checks.append(
            CheckResult(
                name="Launcher wrapper",
                status="WARN",
                detail=f"`{WRAPPER_RELATIVE_PATH}` exists but is not executable.",
                manual_step=f"Run `chmod +x {WRAPPER_RELATIVE_PATH}`.",
            )
        )
        return

    checks.append(
        CheckResult(
            name="Launcher wrapper",
            status="PASS",
            detail=f"`{WRAPPER_RELATIVE_PATH}` is present and executable.",
        )
    )


def check_server_entry(checks: list[CheckResult]) -> None:
    override = os.environ.get("SF_DOCS_MCP_PATH")
    if override:
        if Path(override).is_file():
            checks.append(
                CheckResult(
                    name="sf-docs server entry",
                    status="PASS",
                    detail=f"`SF_DOCS_MCP_PATH` resolves to an existing file at `{override}`.",
                )
            )
            return
        checks.append(
            CheckResult(
                name="sf-docs server entry",
                status="FAIL",
                detail=f"`SF_DOCS_MCP_PATH` is set to `{override}` but no file exists there.",
                manual_step="Build the sf-docs-mcp clone or unset SF_DOCS_MCP_PATH.",
            )
        )
        return

    if DEFAULT_SERVER_PATH.is_file():
        checks.append(
            CheckResult(
                name="sf-docs server entry",
                status="PASS",
                detail=f"Found server entry at `{DEFAULT_SERVER_PATH}`.",
            )
        )
        return

    checks.append(
        CheckResult(
            name="sf-docs server entry",
            status="WARN",
            detail=f"No server entry at `{DEFAULT_SERVER_PATH}` and `SF_DOCS_MCP_PATH` is unset.",
            manual_step=(
                "Clone https://github.com/kvirtue123/sf-docs-mcp to ~/.sf-docs-mcp, then run "
                "`npm install && npm run build && npx playwright install chromium`. "
                "See docs/SF_DOCS_MCP_SETUP.md."
            ),
        )
    )


def check_node(checks: list[CheckResult]) -> None:
    if shutil.which("node"):
        checks.append(
            CheckResult(
                name="node runtime",
                status="PASS",
                detail="`node` is available in PATH.",
            )
        )
    else:
        checks.append(
            CheckResult(
                name="node runtime",
                status="WARN",
                detail="`node` not found in PATH.",
                manual_step="Install Node.js (the launcher uses node to run dist/mcp-server.js).",
            )
        )


def build_report(config_path: Path, repo_root: Path) -> dict[str, Any]:
    checks: list[CheckResult] = []
    if check_config_entry(config_path, checks):
        check_wrapper(repo_root, checks)
        check_server_entry(checks)
        check_node(checks)

    return {
        "overallStatus": determine_overall_status(checks),
        "configPath": str(config_path),
        "checks": [asdict(check) for check in checks],
    }


def print_human_report(report: dict[str, Any]) -> None:
    print(f"sf-docs MCP readiness: {report['overallStatus']}")
    print()
    for check in report["checks"]:
        print(f"- [{check['status']}] {check['name']}: {check['detail']}")
        if check.get("manual_step"):
            print(f"  Next step: {check['manual_step']}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate the project-local Salesforce docs MCP configuration."
    )
    parser.add_argument(
        "--config-path",
        default=".mcp.json",
        help="Path to the project MCP config. Defaults to `.mcp.json` in the current directory.",
    )
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config_path = Path(args.config_path).expanduser().resolve()
    repo_root = config_path.parent
    report = build_report(config_path, repo_root)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_human_report(report)

    if report["overallStatus"] == "ERROR":
        return 2
    if report["overallStatus"] == "FAIL":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
