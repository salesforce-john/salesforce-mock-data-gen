---
name: salesforce-metadata
description: Designs, inspects, and updates Salesforce metadata such as objects, fields, layouts, record types, validation rules, and permission-aware supporting assets. Use when the user needs schema discovery, metadata generation, or metadata edits before Flow, LWC, Apex, or deploy work.
---
# Salesforce Metadata

## Workflow

1. Classify the request first: inspect existing metadata, generate new metadata, or refine existing metadata.
2. Start from the smallest source of truth that can answer the question:
   - local metadata files first
   - org-backed inspection only when the project has a local target org or the user explicitly provides an org alias
3. Use Salesforce MCP before `sf` CLI when org-backed inspection is required.
4. If the change introduces or changes objects, fields, record types, page layouts, or validation rules, identify the downstream access and automation impact before editing.
5. Use `reference.md` when the request needs a compact metadata/admin follow-through pass across validation rules, page-layout or FlexiPage implications, and permission/access impact.
6. When a Salesforce demo scene depends on a Lightning app shell, treat the shell as one default metadata bundle unless the project documents an exception:
   - `CustomApplication` metadata
   - landing or home `FlexiPage`
   - presenter permission-set app visibility
   - any required tab visibility or adjacent access
   - one named launcher path for the connected presenter user
7. Prefer additive metadata changes and preserve existing project conventions unless the user explicitly asks for a structural cleanup.
8. When new objects or fields are introduced, hand off permission follow-through to `field-level-security`.
9. When schema decisions are stable, hand off implementation work to the adjacent build skill:
   - `salesforce-flow` for declarative automation
   - `salesforce-lwc` for UI work
   - `salesforce-apex` for code-backed logic
   - `salesforce-deploy` for validation and rollout
10. End with a short report: metadata touched, access impact, dependent surfaces, app-shell bundle implications when relevant, and next verification step.

## Guardrails

- Stay org-agnostic in the Boilerplate source workspace.
- Do not use a global default org; require a project-local target org or explicit alias for org-backed inspection.
- Prefer permission sets over profile-centric access changes when new fields or objects are involved.
- For demo-critical Lightning app shells, default to permission-set-first app visibility rather than profile-centric app access.
- Do not treat object CRUD as sufficient when field visibility is part of the outcome.
- Do not split app metadata, landing-page placement, and presenter app visibility into separate "later" tasks when a live scene depends on that shell unless the project explicitly documents the exception.
- Do not invent metadata structure when the local project already shows an established convention.

## Routing Smoke Tests

Should trigger:
- `Add a custom object and the supporting fields for this workflow.`
- `Inspect the existing Opportunity metadata before we build automation.`
- `Create a validation rule and page-layout updates for this process.`

Should not trigger:
- `Build a screen flow for this intake process.`
- `Create the Apex invocable that backs this action.`
- `Validate and deploy these metadata changes.`

## Reference

- `.claude/skills/salesforce-metadata/reference.md`
- `.claude/skills/field-level-security/SKILL.md`
