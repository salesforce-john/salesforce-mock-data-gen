---
name: agentforce-observability
description: Diagnoses Agentforce preview and post-deploy behavior using local traces first, with optional live session telemetry when available. Use when preview behavior diverges, regressions are hard to reproduce, quality drifts after launch, or live Agentforce diagnosis is needed.
---
# Agentforce Observability

## Workflow

1. Classify the issue first: preview-only failure, post-deploy regression, environment or permissions problem, or suspected wiring problem.
2. Re-establish expected behavior from the current Builder configuration, Agent Script, legacy YAML artifact if present, recent changes, and any known regression report before proposing fixes.
3. If no local target org is configured yet, stop at local diagnosis and hypothesis building. Do not run org-backed Salesforce MCP or `sf` commands unless the project has a local target org or the user explicitly provides an org alias.
4. Before new org-backed Agentforce diagnosis, run `python scripts/check_org_readiness.py`.
5. Use Salesforce MCP first for org-backed inspection or trace-related work. Fall back to `sf` CLI only when MCP coverage is missing or fails under the same org preconditions.
6. Prefer local preview traces and reproducible sessions first. Reproduce the failing path and at least one neighboring path before changing implementation guidance.
7. Check for gradual quality drift as well as hard failures. Stale grounding, changed business rules, or fragile instructions can require tuning even when deployment technically succeeded.
8. Use STDM, Data Cloud, or helper Apex only when simpler local-trace evidence is insufficient and the target org actually supports that path.
9. Map findings to a specific fix surface: Builder instructions, Agent Script, grounding or semantic-layer setup, legacy YAML artifact, backing logic, Agent Builder wiring, permissions or readiness, or deployment lifecycle.
10. After identifying or applying a fix, hand repeatable regression coverage back to `agentforce-testing` when the issue deserves a saved suite.

## Guardrails

- Local traces are the default path; live telemetry is optional, not the baseline requirement.
- Preserve the same org gate and readiness rules that apply to `agentforce-dx`.
- Do not present observability as a reason to broaden tool access or skip MCP-first behavior.
- Do not assume a successful deploy ended the lifecycle; observability can and should feed new design or tuning work.
- If the request is actually about repeatable smoke coverage, saved regression suites, or broader simulations, route to `agentforce-testing`.
- If the request is actually to build, update, or deploy the agent, route back to `agentforce-dx`.

## Reference

- `.claude/skills/agentforce-dx/reference.md`
- `docs/AGENTFORCE_DX_CHECKLIST.md`
