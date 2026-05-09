#!/usr/bin/env python3
"""
Audit AI org readiness for the connected Salesforce org.

By default, this script verifies the active org and connected user. It can also
assign missing permission sets after explicit confirmation.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET


METADATA_NS = {"sf": "http://soap.sforce.com/2006/04/metadata"}
SETTINGS_COMPONENTS = [
    "AgentPlatform",
    "EinsteinAI",
    "EinsteinCopilot",
    "EinsteinGpt",
    "SecurityHub",
]

PERMISSION_SET_REQUIREMENTS = [
    {
        "label": "Agentforce Default Admin",
        "labels": ["Agentforce Default Admin"],
        "api_names": ["CopilotSalesforceAdmin"],
    },
    {
        "label": "Data Cloud Admin",
        "labels": ["Data Cloud Admin"],
        "api_names": ["CDPAdmin"],
    },
    {
        "label": "Data Cloud Marketing Admin",
        "labels": ["Data Cloud Marketing Admin", "(Legacy) Data Cloud Marketing Admin"],
        "api_names": ["Data_Cloud_Marketing_Admin", "GenieMarketingAdmin"],
    },
]


@dataclass
class CheckResult:
    name: str
    status: str
    detail: str
    fix_available: bool = False
    manual_step: str | None = None


def quote_soql(value: str) -> str:
    return value.replace("\\", "\\\\").replace("'", "\\'")


def run_sf(command: list[str]) -> dict[str, Any]:
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stdout.strip() or result.stderr.strip() or "Salesforce CLI command failed.")

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Could not parse Salesforce CLI JSON output for: {' '.join(command)}") from exc


def sf_query(target_org: str, query: str, *, tooling: bool = False) -> list[dict[str, Any]]:
    command = [
        "sf",
        "data",
        "query",
        "--target-org",
        target_org,
        "--query",
        query,
        "--json",
    ]
    if tooling:
        command.insert(3, "--use-tooling-api")

    payload = run_sf(command)
    return payload["result"]["records"]


def resolve_target_org(target_org: str | None) -> dict[str, str]:
    command = ["sf", "org", "display", "--verbose", "--json"]
    if target_org:
        command[3:3] = ["--target-org", target_org]

    payload = run_sf(command)
    result = payload["result"]
    return {
        "alias": result.get("alias") or "",
        "id": result["id"],
        "instance_url": result["instanceUrl"],
        "username": result["username"],
        "target_org": target_org or result.get("alias") or result["username"],
    }


def retrieve_settings(target_org: str) -> Path:
    temp_dir = Path(tempfile.mkdtemp(prefix="org-readiness-"))
    command = [
        "sf",
        "project",
        "retrieve",
        "start",
        "--target-org",
        target_org,
        "--target-metadata-dir",
        str(temp_dir),
        "--unzip",
        "--json",
    ]
    for component in SETTINGS_COMPONENTS:
        command.extend(["--metadata", f"Settings:{component}"])

    run_sf(command)

    settings_dir_candidates = list(temp_dir.glob("**/settings"))
    if not settings_dir_candidates:
        raise RuntimeError("Retrieved settings metadata but could not find the settings directory.")

    return settings_dir_candidates[0]


def read_setting_value(settings_dir: Path, filename: str, field_name: str) -> str | None:
    candidates = list(settings_dir.glob(f"{filename}.settings"))
    if not candidates:
        candidates = list(settings_dir.glob(f"**/{filename}.settings"))
    if not candidates:
        return None

    root = ET.fromstring(candidates[0].read_text(encoding="utf-8"))
    element = root.find(f"sf:{field_name}", METADATA_NS)
    return element.text if element is not None else None


def collect_permission_sets(target_org: str) -> list[CheckResult]:
    labels = sorted({label for req in PERMISSION_SET_REQUIREMENTS for label in req["labels"]})
    api_names = sorted({name for req in PERMISSION_SET_REQUIREMENTS for name in req["api_names"]})
    username = resolve_target_org(target_org)["username"]

    label_filter = ", ".join(f"'{quote_soql(label)}'" for label in labels)
    api_filter = ", ".join(f"'{quote_soql(name)}'" for name in api_names)

    permission_sets = sf_query(
        target_org,
        (
            "SELECT Id, Name, Label FROM PermissionSet "
            f"WHERE Label IN ({label_filter}) OR Name IN ({api_filter})"
        ),
    )

    permset_by_id = {row["Id"]: row for row in permission_sets}
    permission_set_id_filter = ", ".join(f"'{quote_soql(permission_set_id)}'" for permission_set_id in permset_by_id)
    assignments = sf_query(
        target_org,
        (
            "SELECT PermissionSetId FROM PermissionSetAssignment "
            f"WHERE Assignee.Username = '{quote_soql(username)}' "
            f"AND PermissionSetId IN ({permission_set_id_filter})"
        ),
    ) if permset_by_id else []
    assigned_ids = {row["PermissionSetId"] for row in assignments}

    results: list[CheckResult] = []
    for requirement in PERMISSION_SET_REQUIREMENTS:
        matches = [
            row for row in permission_sets
            if row["Label"] in requirement["labels"] or row["Name"] in requirement["api_names"]
        ]
        if not matches:
            results.append(
                CheckResult(
                    name=requirement["label"],
                    status="WARN",
                    detail="Permission set is not available in this org.",
                )
            )
            continue

        assigned_match = next((row for row in matches if row["Id"] in assigned_ids), None)
        if assigned_match:
            label = assigned_match["Label"]
            detail = f"Assigned to the connected user via `{assigned_match['Name']}` ({label})."
            if label != requirement["label"]:
                detail += " Using an accepted legacy equivalent."
            results.append(CheckResult(name=requirement["label"], status="PASS", detail=detail))
            continue

        match_names = ", ".join(f"`{row['Name']}` ({row['Label']})" for row in matches)
        results.append(
            CheckResult(
                name=requirement["label"],
                status="FAIL",
                detail=f"Available in org but not assigned to the connected user: {match_names}.",
                fix_available=True,
            )
        )

    return results


def collect_setting_checks(target_org: str) -> list[CheckResult]:
    settings_dir = retrieve_settings(target_org)
    prompt_builder = read_setting_value(settings_dir, "EinsteinGpt", "enableEinsteinGptPlatform")
    agentforce = read_setting_value(settings_dir, "AgentPlatform", "enableAgentPlatform")
    copilot = read_setting_value(settings_dir, "EinsteinCopilot", "enableEinsteinGptCopilot")
    llm_gateway_proxy = read_setting_value(settings_dir, "SecurityHub", "aiGatewayUsageMetric")

    results = [
        CheckResult(
            name="Prompt Builder",
            status="PASS" if prompt_builder == "true" else "FAIL",
            detail=(
                "Einstein GPT platform is enabled."
                if prompt_builder == "true"
                else "Enable Prompt Builder / Einstein GPT platform in Setup."
            ),
        ),
        CheckResult(
            name="Einstein / Agentforce",
            status="PASS" if agentforce == "true" else "FAIL",
            detail=(
                "Agent Platform is enabled."
                if agentforce == "true"
                else "Enable Agentforce from Setup > Salesforce Go > Agentforce (Default) > Get Started > Turn On."
            ),
        ),
    ]

    if copilot == "true":
        results.append(
            CheckResult(
                name="Agentforce Copilot Surface",
                status="PASS",
                detail="Einstein Copilot is enabled.",
            )
        )
    elif copilot == "false":
        results.append(
            CheckResult(
                name="Agentforce Copilot Surface",
                status="WARN",
                detail="Einstein Copilot is disabled. Agent Platform can still be on, but the agent surface may need review.",
            )
        )

    if llm_gateway_proxy == "true":
        results.append(
            CheckResult(
                name="Einstein LLM Gateway",
                status="PASS",
                detail="Metadata proxy `SecurityHub.aiGatewayUsageMetric` is enabled.",
            )
        )
    else:
        results.append(
            CheckResult(
                name="Einstein LLM Gateway",
                status="MANUAL",
                detail=(
                    "No stable CLI/MCP toggle surfaced for the Advanced Settings check. "
                    "Current metadata proxy `SecurityHub.aiGatewayUsageMetric` is not enabled."
                ),
                manual_step="Verify Setup > Advanced Settings > Einstein LLM Gateway manually.",
            )
        )

    return results


def overall_status(results: list[CheckResult]) -> str:
    if any(result.status == "FAIL" for result in results):
        return "FAIL"
    if any(result.status == "MANUAL" for result in results):
        return "WARN"
    if any(result.status == "WARN" for result in results):
        return "WARN"
    return "PASS"


def maybe_assign_missing_permission_sets(
    target_org: str,
    username: str,
    results: list[CheckResult],
    *,
    assume_yes: bool = False,
) -> bool:
    missing = [result for result in results if result.fix_available]
    if not missing:
        return False

    labels = [result.name for result in missing]
    label_lookup = {requirement["label"]: requirement for requirement in PERMISSION_SET_REQUIREMENTS}
    label_filter = ", ".join(f"'{quote_soql(label)}'" for label in labels)
    api_filter = ", ".join(
        f"'{quote_soql(api_name)}'"
        for requirement in PERMISSION_SET_REQUIREMENTS
        for api_name in requirement["api_names"]
    )
    query = (
        "SELECT Name, Label FROM PermissionSet "
        f"WHERE Label IN ({label_filter}) "
        f"OR Name IN ({api_filter})"
    )
    definitions = sf_query(target_org, query)

    to_assign: list[str] = []
    for result in missing:
        requirement = label_lookup[result.name]
        matches = [
            row for row in definitions
            if row["Label"] in requirement["labels"] or row["Name"] in requirement["api_names"]
        ]
        if len(matches) == 1:
            to_assign.append(matches[0]["Name"])

    if not to_assign:
        return False

    if not assume_yes:
        answer = input(
            "Assign missing permission sets to the connected user "
            f"({username}) in `{target_org}`? [y/N]: "
        ).strip().lower()
        if answer not in {"y", "yes"}:
            return False

    command = [
        "sf",
        "org",
        "assign",
        "permset",
        "--target-org",
        target_org,
        "--on-behalf-of",
        username,
        "--json",
    ]
    for permset_name in to_assign:
        command.extend(["--name", permset_name])
    run_sf(command)
    return True


def build_report(target_org: dict[str, str], results: list[CheckResult]) -> dict[str, Any]:
    return {
        "overallStatus": overall_status(results),
        "targetOrg": target_org["target_org"],
        "connectedUser": target_org["username"],
        "checks": [asdict(result) for result in results],
    }


def print_human_report(report: dict[str, Any]) -> None:
    print(f"Target org: {report['targetOrg']}")
    print(f"Connected user: {report['connectedUser']}")
    print(f"Overall status: {report['overallStatus']}")
    print("")
    for check in report["checks"]:
        print(f"[{check['status']}] {check['name']}: {check['detail']}")
        if check.get("manual_step"):
            print(f"  Manual step: {check['manual_step']}")


def run_audit(target_org: str) -> tuple[dict[str, str], list[CheckResult]]:
    org_details = resolve_target_org(target_org)
    results = collect_setting_checks(org_details["target_org"])
    results.extend(collect_permission_sets(org_details["target_org"]))
    return org_details, results


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify Prompt Builder, Agentforce, LLM gateway guidance, and connected-user permission sets."
    )
    parser.add_argument("--target-org", help="Salesforce username or alias. Defaults to the current target org.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")
    parser.add_argument(
        "--assign-missing-permission-sets",
        action="store_true",
        help="Prompt to assign any missing required permission sets to the connected user.",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Skip the interactive confirmation prompt when assigning missing permission sets.",
    )
    args = parser.parse_args()

    try:
        org_details, results = run_audit(args.target_org or "")
        if args.assign_missing_permission_sets:
            assigned = maybe_assign_missing_permission_sets(
                org_details["target_org"],
                org_details["username"],
                results,
                assume_yes=args.yes,
            )
            if assigned:
                org_details, results = run_audit(org_details["target_org"])

        report = build_report(org_details, results)
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print_human_report(report)

        return 1 if report["overallStatus"] == "FAIL" else 0
    except RuntimeError as exc:
        message = {"overallStatus": "ERROR", "error": str(exc)}
        if args.json:
            print(json.dumps(message, indent=2))
        else:
            print(f"Overall status: ERROR\n\n{exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
