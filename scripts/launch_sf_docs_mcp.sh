#!/usr/bin/env bash
# Launch the Salesforce Help / Developer docs MCP server.
#
# Resolution order:
#   1. SF_DOCS_MCP_PATH env override -> use that file path directly.
#   2. ~/.sf-docs-mcp/dist/mcp-server.js (canonical local clone path).
#   3. Error out with install instructions.
#
# All discovery output goes to stderr or /dev/null. Stdout MUST stay clean for
# the MCP stdio protocol.

set -euo pipefail

emit_error() {
  printf 'sf-docs: %s\n' "$1" >&2
}

SERVER_PATH="${SF_DOCS_MCP_PATH:-}"
if [ -z "$SERVER_PATH" ]; then
  SERVER_PATH="$HOME/.sf-docs-mcp/dist/mcp-server.js"
fi

if [ ! -f "$SERVER_PATH" ]; then
  emit_error "Server entry not found at $SERVER_PATH. See docs/SF_DOCS_MCP_SETUP.md (clone https://github.com/kvirtue123/sf-docs-mcp to ~/.sf-docs-mcp and run npm install && npm run build && npx playwright install chromium)."
  exit 1
fi

if ! command -v node >/dev/null 2>&1; then
  emit_error "node not found in PATH. See docs/SF_DOCS_MCP_SETUP.md."
  exit 1
fi

exec node "$SERVER_PATH"
