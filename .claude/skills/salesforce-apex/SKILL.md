---
name: salesforce-apex
description: Designs and updates Salesforce Apex such as classes, triggers, invocables, async jobs, and test classes when code-backed logic is the right implementation boundary. Use when the user needs Apex-specific implementation, review, or repair.
---
# Salesforce Apex

## Workflow

1. Classify the code need first: service, trigger handler, invocable, async job, controller, test class, or targeted refactor of existing trigger/test shape.
2. Confirm Apex is the right boundary:
   - reuse existing logic first
   - prefer metadata and Flow when they are sufficient
   - use Apex when the requirement needs deterministic logic, reuse, scale, integration, or testable code boundaries that low-code should not absorb
3. Inspect the local project shape before authoring:
   - existing handlers and service patterns
   - related schema
   - Flow or LWC callers
   - existing tests
4. If the work depends on new schema, hand off the metadata surface to `salesforce-metadata` first.
5. If Apex is backing a Flow or LWC surface, keep the caller contract explicit and preserve the adjacent handoff.
6. Use Salesforce MCP before `sf` CLI for org-backed inspection or validation, and only when the project has a local target org or explicit alias.
7. Keep tests, sharing, FLS/CRUD, bulkification, and error handling in scope from the start.
8. When refactoring triggers, keep logic out of the trigger body, preserve the project handler pattern, and make the changed behavior easy to cover with focused tests.
9. Define the smallest useful Apex test follow-through for the change:
   - changed path
   - bulk or async behavior when relevant
   - caller contract, sharing, or permission-sensitive behavior when relevant
10. When implementation is ready, hand off validation and rollout to `salesforce-deploy`.
11. End with a short report: code boundary, callers, risks, and next verification step.

## Guardrails

- Stay org-agnostic in the Boilerplate source workspace.
- Do not use org-backed Salesforce MCP or `sf` CLI unless the project has a local target org or the user explicitly provides an org alias.
- Do not default to Apex when Flow or metadata can solve the problem cleanly.
- Keep SOQL and DML out of loops.
- Keep trigger logic out of trigger bodies and preserve project handler patterns.
- Do not treat tests as optional for new or materially changed Apex behavior.
- Do not create low-value tests that merely restate obvious implementation details without protecting a real contract or regression path.

## Routing Smoke Tests

Should trigger:
- `Create an invocable Apex action for this Flow.`
- `Refactor this trigger logic into the project handler pattern.`
- `Build the Apex service and tests behind this integration step.`

Should not trigger:
- `Add the supporting fields for this feature.`
- `Build the declarative Flow wrapper for this action.`
- `Validate and deploy this Apex change.`

## Reference

- `.claude/skills/salesforce-metadata/SKILL.md`
- `.claude/skills/salesforce-flow/SKILL.md`
