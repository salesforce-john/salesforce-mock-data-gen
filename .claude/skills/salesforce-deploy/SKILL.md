---
name: salesforce-deploy
description: Validates and deploys Salesforce metadata changes with project-local org discipline, readiness checks, and post-deploy verification. Use when the user needs deploy planning, validation, rollout sequencing, or post-deploy verification for Salesforce changes.
---
# Salesforce Deploy

## Workflow

1. Classify the deployment job first: validate only, deploy, retrieve, or post-deploy verification.
2. Confirm the target context before any org-backed action:
   - project-local target org, or
   - explicit user-provided org alias
3. Run `python scripts/check_org_readiness.py` before new org-backed deploy or validation work in a target project.
4. Use Salesforce MCP before `sf` CLI where the MCP covers the needed action. Fall back to `sf` only under the same org preconditions.
5. Validate before deploying whenever the change is user-facing, cross-surface, or hard to reverse.
6. Keep the deployment scope as small and explicit as possible.
7. When a Salesforce demo scene depends on a Lightning app shell, validate and deploy the default bundle together whenever possible:
   - `CustomApplication`
   - landing or home `FlexiPage`
   - presenter permission-set app visibility
   - any required tab visibility or adjacent access
8. Verify the changed path and at least one adjacent path after validation or deploy. When the surface is user-visible, hand the proof step to `salesforce-ui-verification`.
9. If the deployed work supports a Salesforce demo, verify the exact launch surface, placed runtime asset, and presenter click path instead of stopping at deploy success.
10. For demo-critical Lightning app shells, treat connected-user App Launcher verification as part of deploy completion:
   - open Salesforce as the connected user
   - open App Launcher
   - launch the named app
   - confirm the shell changes
   - confirm the landing page renders
11. For resolved UI checks, expect durable evidence such as screenshot plus assertion artifact instead of screenshot-only proof.
12. If deployment fails because the build surface is wrong, hand the fix back to the owning implementation skill:
   - `salesforce-metadata`
   - `salesforce-flow`
   - `salesforce-lwc`
   - `salesforce-apex`
   - `agentforce-dx` for agent-specific publish or activation workflows
13. End with a short report: target, scope, validation result, deploy result, UI-verification result when relevant, launcher-verification result when relevant, and next safe step.

## Guardrails

- Stay org-agnostic in the Boilerplate source workspace.
- Do not use a global default org; require a project-local target org or explicit alias.
- Do not skip validation-first behavior for user-facing or shared-path changes unless the user explicitly accepts the risk.
- Do not blur generic metadata deployment with Agentforce-specific publish or activation work; keep `agentforce-dx` as the orchestrator for that lifecycle.
- Do not call a deployment complete without verification evidence.
- For Salesforce demo work, do not call a deployment complete when the launch surface or placed runtime path is still missing.
- For demo-critical Lightning app shells, do not call deployment complete until the connected user can open App Launcher, launch the named app, and see the intended landing shell.
- Do not treat deep-link verification as equivalent to launcher verification when the scene depends on app visibility.
- Do not treat screenshot-only proof as sufficient for resolved UI checks when `salesforce-ui-verification` should be able to emit a structured assertion artifact.

## Routing Smoke Tests

Should trigger:
- `Validate these metadata changes against the target org before we deploy.`
- `Deploy this scoped set of Salesforce changes and verify the adjacent path.`
- `Help me sequence this rollout and post-deploy verification.`

Should not trigger:
- `Create the new fields this release depends on.`
- `Build the screen flow for this process.`
- `Fix the broken agent behavior after deployment.`

## Reference

- `scripts/check_org_readiness.py`
- `.claude/skills/salesforce-ui-verification/SKILL.md`
- `.claude/skills/open-salesforce-org-browser/SKILL.md`
