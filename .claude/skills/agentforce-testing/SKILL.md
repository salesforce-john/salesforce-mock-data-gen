---
name: agentforce-testing
description: Plans and runs repeatable Agentforce smoke, regression, simulation, and Testing Center workflows across the ADLC. Use when the user asks to test an agent, create or maintain saved coverage, add safety probes, validate guardrails, or validate actions in isolation.
---
# Agentforce Testing

## Workflow

1. Start from the changed behavior, current Builder or Agent Script configuration, or saved regression goal and define the smallest useful coverage plan.
2. If the request is still mainly about what to build, how to wire the agent, or how to scope a sandbox or pilot, route back to `agentforce-dx` before expanding coverage.
3. Cover the changed path, at least one adjacent regression path, one off-topic or guardrail case, and one safety-oriented probe when user-facing behavior changed.
4. Include grounding, orchestration, or handoff cases when the change touches enterprise data, multi-agent flows, or escalation behavior.
5. If no local target org is configured yet, stop at local test design and saved suite preparation. Do not run org-backed Salesforce MCP or `sf` commands unless the project has a local target org or the user explicitly provides an org alias.
6. Before new org-backed Agentforce test execution, run `python scripts/check_org_readiness.py`.
7. Use Salesforce MCP first for org-backed test work. Fall back to `sf` CLI only when MCP coverage is missing or fails under the same org preconditions.
8. Prefer preview smoke tests for quick validation during development and validation phases of the ADLC.
9. Use Testing Center or other saved test surfaces for repeatable regression suites, broader simulation passes, or shared team validation.
10. Save reusable test specs under `specs/`, for example `specs/<agent>-smoke.yaml` or `specs/<agent>-regression.yaml`, when the project still uses YAML-based saved coverage or when that is the clearest team convention.
11. Use action-level validation only when isolated Flow, Apex, grounding, or permission behavior needs to be checked separately from full agent routing.
12. Report what was planned, what ran, what passed, what failed, and which issues should move to `agentforce-observability` for deeper diagnosis.

## Guardrails

- Keep tests targeted. Do not add low-value suites that simply restate the implementation.
- Present the planned utterances and assertions before running a broad or destructive test pass.
- Preserve the same org gate and readiness rules that apply to `agentforce-dx`.
- Do not assume saved YAML test assets are the source of truth for all Agentforce projects; use them when helpful, not as a doctrinal default.
- If the request is mainly about build, deploy, sandbox scope, or handoff planning, route to `agentforce-dx`.
- If the request is mainly about why preview or live behavior is wrong, route to `agentforce-observability`.

## Reference

- `docs/AGENTFORCE_DX_CHECKLIST.md`
- `.claude/skills/agentforce-dx/reference.md`
