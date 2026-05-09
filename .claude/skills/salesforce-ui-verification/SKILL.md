---
name: salesforce-ui-verification
description: Verifies Salesforce Lightning UI state with Playwright MCP, durable evidence bundles, and Salesforce-specific checks such as App Launcher, app shell, landing state, featured object, and KPI plausibility.
---
# Salesforce UI Verification

## When To Use

- The user asks to verify what is actually visible in Salesforce.
- A deploy or validation flow needs proof that a Lightning surface rendered correctly.
- A demo scene needs connected-user App Launcher proof, landing-state proof, or presenter-path proof.
- A build task is user-facing enough that deploy success is not sufficient evidence.

## Primary Tooling

- Cursor built-in browser (`mcp__plugin_browser_browser__*`) is the primary browser verifier.
- `salesforce-dx` remains the authority for org metadata, data, users, and tests.
- `open-salesforce-org-browser` is the manual fallback, not the verifier.
- No external Playwright installation or browser extension is required.

## Workflow

1. Confirm the org precondition:
   - project-local target org in `.sf/config.json` or `.sfdx/sfdx-config.json`, or
   - explicit user-provided org alias.
2. Confirm the browser-verification precondition:
   - the Cursor built-in browser is available (`mcp__plugin_browser_browser__*` tools)
3. Prefer attach-to-existing-browser verification first:
   - reuse the connected user's authenticated browser session
   - attach to the already-open Salesforce tab when possible
   - stop and report if auth or browser approval needs manual user action
4. Define the exact check before touching the page:
   - `checkId`
   - `checkType`
   - `targetSurface`
   - `expectedVisibleCues`
   - the durable evidence location
5. Use Salesforce-specific verification paths instead of generic deep links when the scene depends on visibility:
   - `presenter path`: verify the real click path the user will follow
   - `app shell`: verify App Launcher -> named app -> immediate landing state
   - `featured object`: verify the intended object, list, or record surface renders with the expected cues
   - `kpi plausibility`: verify that the visible metric state matches the demo story and labeled basis
6. Capture a durable evidence bundle for every resolved UI check:
   - screenshot under the repo-managed proof folder
   - assertion JSON artifact with the structured result
   - optional console/network note when it explains a failure or edge case
   - optional metadata corroboration from `salesforce-dx`
7. For demo-linked work, keep proof under the active run folder:
   - `docs/_demo_working/<demo-slug>-<YYYYMMDD-HHMM>/proof/`
8. When verification fails, return:
   - what page or surface was attempted
   - which expected cue was missing
   - whether the failure looks like auth, visibility, placement, data, or rendering
   - the next owning lane, such as `salesforce-deploy`, `salesforce-metadata`, `salesforce-flow`, `salesforce-lwc`, `salesforce-apex`, or `salesforce-ux-designer`

## Evidence Contract

For a resolved UI verification row, the `Evidence` field should reference both:

- one screenshot file such as `proof/02-app-shell.png`
- one assertion artifact such as `proof/02-app-shell-assertion.json`

Suggested assertion JSON payload:

```json
{
  "checkId": "PV2",
  "checkType": "app shell",
  "targetSurface": "Service Console",
  "expectedVisibleCues": [
    "Intake screen flow"
  ],
  "actualResult": "App Launcher opened Service Console and landed on Intake screen flow.",
  "status": "pass",
  "screenshotPath": "proof/02-app-shell.png",
  "verifiedAt": "2026-05-04T17:00:00+00:00",
  "verificationTool": "playwright",
  "metadataCorroboration": "Service Console app assigned via Intake_Demo_User permission set",
  "consoleOrNetworkNotes": ""
}
```

Keep `expectedVisibleCues` specific enough that another agent can tell whether the same surface actually rendered.

## Guardrails

- Do not treat a deep link as equivalent to connected-user App Launcher proof when app visibility matters.
- Do not call a UI check done with screenshots alone; resolved checks need a screenshot plus assertion artifact.
- Do not leave the immediate landing state implicit for `app shell` verification.
- Do not rely on Playwright alone when metadata corroboration would resolve ambiguity about visibility, placement, or permissions.
- Do not keep retrying failing browser actions without new evidence. If auth, browser approval, or session handoff requires user action, stop and report it.
- Do not treat `open-salesforce-org-browser` as proof that the verified surface is correct.

## Related References

- `docs/SALESFORCE_UI_VERIFICATION_OPERATOR.md`
- `docs/MCP_CONNECTION_HEALTH.md`
- `.claude/skills/open-salesforce-org-browser/SKILL.md`
- `.claude/skills/salesforce-deploy/SKILL.md`
- `.claude/skills/demo-audit/SKILL.md`
- `docs/DEMO_READINESS_OPERATOR.md`

## Routing Smoke Tests

Should trigger:

- `Verify that this Lightning app actually opens from App Launcher and lands on the intended page.`
- `Prove the presenter path is visible in Salesforce, not just deployed.`
- `Check whether the record page really shows the cues we need for the demo.`

Should not trigger:

- `Open the default connected org in Cursor.`
- `Deploy this metadata bundle to the target org.`
- `Create the flow that powers this demo scene.`
