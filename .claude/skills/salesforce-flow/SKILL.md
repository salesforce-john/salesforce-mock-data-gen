---
name: salesforce-flow
description: Designs and updates Salesforce Flow solutions, especially screen, record-triggered, scheduled, and action-wrapper flows. Use when the user needs declarative automation, guided user journeys, or Flow-backed actions before escalating to Apex.
---
# Salesforce Flow

## Workflow

1. Classify the Flow need first: screen, record-triggered, scheduled, autolaunched, or agent/action wrapper.
2. Confirm Flow is still the right fit:
   - prefer low-code first
   - escalate to `salesforce-apex` only when deterministic complexity, scale, or reuse clearly exceeds what Flow should own
3. Inspect local project patterns before authoring:
   - existing flows
   - related schema or actions
   - existing screen or page UX decisions
4. If the work depends on new schema, hand off the metadata surface first to `salesforce-metadata`.
5. Keep screens role-focused and easy to complete. If the request is primarily about layout or interaction design, take guidance from `salesforce-ux-designer` before finalizing the Flow shape.
6. Use Salesforce MCP before `sf` CLI for org-backed inspection or validation, and only when the project has a local target org or explicit alias.
7. Keep validation, branching, error paths, and finish behavior explicit in the design.
8. When Flow needs backing logic or invocable behavior, hand off that part to `salesforce-apex`.
9. When the Flow is ready for validation or rollout, hand off to `salesforce-deploy`.
10. End with a short report: flow type, user path or trigger logic, dependencies, and the next verification step.

## Guardrails

- Stay org-agnostic in the Boilerplate source workspace.
- Do not use org-backed Salesforce MCP or `sf` CLI unless the project has a local target org or the user explicitly provides an org alias.
- Prefer focused declarative automation over stacking multiple competing automations on the same path.
- Do not hide a real Apex requirement behind an overgrown Flow; explain when code is the better boundary.
- Keep user-facing behavior testable, especially screens, branches, errors, and completion states.

## Routing Smoke Tests

Should trigger:
- `Build a screen flow for account intake with branching and finish behavior.`
- `Create a record-triggered flow for opportunity handoff.`
- `Wrap this action in a Flow before we wire it to Agentforce.`

Should not trigger:
- `Add the custom fields this flow depends on.`
- `Create the Apex invocable this flow should call.`
- `Validate and deploy this Flow to the target org.`

## Reference

- `.claude/skills/salesforce-ux-designer/SKILL.md`
