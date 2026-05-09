#!/usr/bin/env python3
"""
Validate the project-local Firecrawl MCP configuration.

This checker is intentionally narrow: it validates the committed Boilerplate
`.mcp.json` contract for the hosted Firecrawl MCP without attempting any
network calls or silent repairs.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


FIRECRAWL_SERVER_KEY = "firecrawl-heroku"
FIRECRAWL_URL = "https://firecrawl-0076d0033d53.herokuapp.com"
EXPECTED_COMMAND = "npx"
EXPECTED_ARGS = ["-y", "firecrawl-mcp"]


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


def build_report(config_path: Path) -> dict[str, Any]:
    checks: list[CheckResult] = []

    if config_path.exists():
        checks.append(
            CheckResult(
                name="Project MCP config file",
                status="PASS",
                detail=f"Found project MCP config at `{config_path}`.",
            )
        )
    else:
        checks.append(
            CheckResult(
                name="Project MCP config file",
                status="FAIL",
                detail=f"Project MCP config is missing: `{config_path}`.",
                manual_step="Restore the committed `.mcp.json` file before relying on Firecrawl.",
            )
        )
        return {
            "overallStatus": determine_overall_status(checks),
            "configPath": str(config_path),
            "checks": [asdict(check) for check in checks],
        }

    try:
        config = read_json(config_path)
    except RuntimeError as exc:
        checks.append(CheckResult(name="Project MCP config JSON", status="ERROR", detail=str(exc)))
        return {
            "overallStatus": determine_overall_status(checks),
            "configPath": str(config_path),
            "checks": [asdict(check) for check in checks],
        }

    mcp_servers = config.get("mcpServers")
    if not isinstance(mcp_servers, dict):
        checks.append(
            CheckResult(
                name="MCP servers object",
                status="FAIL",
                detail="`mcpServers` is missing or not an object in `.mcp.json`.",
                manual_step="Restore the Boilerplate MCP structure before using Firecrawl.",
            )
        )
        return {
            "overallStatus": determine_overall_status(checks),
            "configPath": str(config_path),
            "checks": [asdict(check) for check in checks],
        }

    firecrawl_server = mcp_servers.get(FIRECRAWL_SERVER_KEY)
    if not isinstance(firecrawl_server, dict):
        checks.append(
            CheckResult(
                name="Firecrawl server entry",
                status="FAIL",
                detail="No `firecrawl-heroku` server entry is configured in `.mcp.json`.",
                manual_step="Restore the committed Firecrawl MCP entry before relying on Firecrawl.",
            )
        )
        return {
            "overallStatus": determine_overall_status(checks),
            "configPath": str(config_path),
            "checks": [asdict(check) for check in checks],
        }

    command = firecrawl_server.get("command")
    args = firecrawl_server.get("args")
    if command == EXPECTED_COMMAND and isinstance(args, list) and [str(arg) for arg in args] == EXPECTED_ARGS:
        checks.append(
            CheckResult(
                name="Firecrawl launch command",
                status="PASS",
                detail="Configured for the expected `npx -y firecrawl-mcp` launch path.",
            )
        )
    else:
        checks.append(
            CheckResult(
                name="Firecrawl launch command",
                status="FAIL",
                detail="Firecrawl is configured, but not with the expected `npx -y firecrawl-mcp` command.",
                manual_step="Restore the Boilerplate Firecrawl server definition in `.mcp.json`.",
            )
        )

    env = firecrawl_server.get("env")
    if not isinstance(env, dict):
        checks.append(
            CheckResult(
                name="Firecrawl environment",
                status="FAIL",
                detail="Firecrawl `env` is missing or not an object.",
                manual_step="Set `FIRECRAWL_API_URL` to the hosted app base URL in `.mcp.json`.",
            )
        )
        return {
            "overallStatus": determine_overall_status(checks),
            "configPath": str(config_path),
            "checks": [asdict(check) for check in checks],
        }

    configured_url = env.get("FIRECRAWL_API_URL")
    if configured_url == FIRECRAWL_URL:
        checks.append(
            CheckResult(
                name="Firecrawl API URL",
                status="PASS",
                detail=f"`FIRECRAWL_API_URL` matches the hosted base URL `{FIRECRAWL_URL}`.",
            )
        )
    elif configured_url == f"{FIRECRAWL_URL}/v1":
        checks.append(
            CheckResult(
                name="Firecrawl API URL",
                status="FAIL",
                detail="`FIRECRAWL_API_URL` incorrectly points at `/v1` instead of the hosted app base URL.",
                manual_step="Use the app base URL without `/v1` in `.mcp.json`.",
            )
        )
    else:
        checks.append(
            CheckResult(
                name="Firecrawl API URL",
                status="FAIL",
                detail="`FIRECRAWL_API_URL` does not match the expected hosted Firecrawl URL.",
                manual_step=f"Set `FIRECRAWL_API_URL` to `{FIRECRAWL_URL}` in `.mcp.json`.",
            )
        )

    if "FIRECRAWL_API_KEY" not in env:
        checks.append(
            CheckResult(
                name="Firecrawl API key handling",
                status="PASS",
                detail="`FIRECRAWL_API_KEY` is omitted from the committed config, which is correct for the current hosted setup.",
            )
        )
    else:
        checks.append(
            CheckResult(
                name="Firecrawl API key handling",
                status="WARN",
                detail="`FIRECRAWL_API_KEY` is present in `.mcp.json`.",
                manual_step=(
                    "Keep real Firecrawl secrets out of committed files. Omit the key unless the hosted instance "
                    "enforces auth and you are supplying it through a secure local-only path."
                ),
            )
        )

    return {
        "overallStatus": determine_overall_status(checks),
        "configPath": str(config_path),
        "checks": [asdict(check) for check in checks],
    }


def print_human_report(report: dict[str, Any]) -> None:
    print(f"Firecrawl MCP readiness: {report['overallStatus']}")
    print()
    for check in report["checks"]:
        print(f"- [{check['status']}] {check['name']}: {check['detail']}")
        if check.get("manual_step"):
            print(f"  Next step: {check['manual_step']}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate the project-local Firecrawl MCP configuration."
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
    report = build_report(Path(args.config_path).expanduser().resolve())
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
