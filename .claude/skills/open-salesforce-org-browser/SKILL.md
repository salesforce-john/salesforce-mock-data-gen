---
name: open-salesforce-org-browser
description: Opens the default connected Salesforce org in Cursor Simple Browser. Use when the user asks to open the default org, connected org, Salesforce org, Lightning page, or a Salesforce URL inside Cursor browser or Simple Browser.
---
# Open Salesforce Org Browser

Use this skill to open Salesforce in Cursor. If the task is to prove what is visible on the page, verify App Launcher behavior, or capture durable UI evidence, use `salesforce-ui-verification` instead.

## Workflow

1. Default to the Lightning home page unless the user asks for a specific Salesforce path.
2. Run the helper script:
   `bash .claude/skills/open-salesforce-org-browser/scripts/open_default_org.sh`
3. To open a specific page, pass a path such as:
   `bash .claude/skills/open-salesforce-org-browser/scripts/open_default_org.sh "lightning/o/Account/list"`
4. When the task is demo-critical Lightning app-shell verification, prefer the real launcher path over a deep link:
   - open Salesforce as the connected user
   - open App Launcher
   - select the named app
   - confirm the shell changes
   - confirm the landing page renders
5. Confirm that the page or app shell was opened in Cursor.
6. If UI automation fails, give the manual fallback:
   - Press `Cmd+Shift+P`
   - Run `Simple Browser: Show`
   - Paste a fresh URL generated with `sf org open --url-only --path <path> --json`

## Guardrails

- Require a project-local target org in `.sf/config.json` or `.sfdx/sfdx-config.json` unless the user explicitly asks for another org.
- Do not rely on a global default org for this skill.
- Do not treat this skill as a substitute for `salesforce-ui-verification` when the job is proof rather than opening.
- Do not treat a direct deep link as proof that a Lightning app is visible to the connected user in App Launcher.
- For demo-critical Lightning app shells, keep proof focused on the named app, the shell change, and the landing page the presenter will actually show.
- Do not print or share the frontdoor URL unless the user explicitly needs the manual fallback.
- This skill requires Salesforce CLI auth and macOS Accessibility permissions for Cursor automation.
