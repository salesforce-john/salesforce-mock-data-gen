---
name: diagnostic-refresh
description: Runs deep root-cause analysis and remediation for Salesforce bugs, deployment failures, and regression issues. Use when simple fixes failed, the user is debugging, or a durable fix needs proof.
---
# Diagnostic Refresh

## Workflow

1. Establish a read-only baseline of org state, logs, and recent metadata changes.
2. Define expected behavior and isolate a minimal failing case.
3. Form a root-cause hypothesis and prove or disprove it with safe experiments.
4. Apply the smallest durable fix only after the cause is confirmed.
5. Re-run the failing path and broader regression checks.
6. Report root cause, remediation, evidence, and residual risk.

## Guardrails

- Do not patch symptoms without evidence.
- Fix shared consumers when the defect sits in shared metadata or utilities.
- Prefer platform-native patterns over brittle custom workarounds.
