#!/usr/bin/env bash
set -euo pipefail

SALESFORCE_PATH="${1:-lightning}"
WORKSPACE_ROOT="${CURSOR_WORKSPACE_ROOT:-$(pwd)}"
LOCAL_TARGET_ORG=""

if ! command -v sf >/dev/null 2>&1; then
  echo "Salesforce CLI (sf) is not available on PATH." >&2
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required to parse the Salesforce CLI JSON response." >&2
  exit 1
fi

if ! command -v osascript >/dev/null 2>&1; then
  echo "osascript is required for Cursor browser automation on macOS." >&2
  exit 1
fi

if [[ -f "$WORKSPACE_ROOT/.sf/config.json" ]]; then
  LOCAL_TARGET_ORG="$(python3 -c 'import json, pathlib, sys; data = json.loads(pathlib.Path(sys.argv[1]).read_text()); print(data.get("target-org", ""))' "$WORKSPACE_ROOT/.sf/config.json")"
fi

if [[ -z "$LOCAL_TARGET_ORG" && -f "$WORKSPACE_ROOT/.sfdx/sfdx-config.json" ]]; then
  LOCAL_TARGET_ORG="$(python3 -c 'import json, pathlib, sys; data = json.loads(pathlib.Path(sys.argv[1]).read_text()); print(data.get("defaultusername", ""))' "$WORKSPACE_ROOT/.sfdx/sfdx-config.json")"
fi

if [[ -z "$LOCAL_TARGET_ORG" ]]; then
  echo "No project-local Salesforce target org is configured in .sf/config.json or .sfdx/sfdx-config.json." >&2
  echo "Authorize or set a target org in this project before opening the org browser." >&2
  exit 1
fi

ORG_JSON="$(sf org open --target-org "$LOCAL_TARGET_ORG" --url-only --path "$SALESFORCE_PATH" --json)"
ORG_URL="$(python3 -c 'import json, sys; print(json.load(sys.stdin)["result"]["url"])' <<<"$ORG_JSON")"
ORG_USERNAME="$(python3 -c 'import json, sys; print(json.load(sys.stdin)["result"]["username"])' <<<"$ORG_JSON")"

osascript - "$ORG_URL" <<'OSA'
on run argv
    set orgUrl to item 1 of argv

    tell application "Cursor" to activate
    delay 0.5

    tell application "System Events"
        keystroke "p" using {command down, shift down}
        delay 0.5
        keystroke "Simple Browser: Show"
        delay 0.5
        key code 36
        delay 0.7
        keystroke orgUrl
        delay 0.3
        key code 36
    end tell
end run
OSA

echo "Opened default org for ${ORG_USERNAME} in Cursor Simple Browser."
