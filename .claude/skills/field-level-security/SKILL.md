---
name: field-level-security
description: Updates profiles and permission sets when the primary job is field visibility, object access, or permission follow-through after schema or feature changes. Use when the user asks to update FLS, visibility, permission sets, or access grants. Do not use as the first stop for creating new schema.
---
# Field Level Security

## Workflow

1. Confirm the primary job is access follow-through, not schema design.
2. Detect the new or changed objects, fields, page surfaces, or access requirements that drove the request.
3. If the request started as schema work, read the `salesforce-metadata` compact-core reference so the access updates stay aligned with the metadata follow-through.
4. Identify which profiles and permission sets should gain access.
5. When a demo-critical Lightning app shell is part of the presenter path, update the presenter permission set in the same pass for:
   - `applicationVisibilities`
   - any required tabs
   - the object and field access needed on the landing path
6. Add object and field permissions without removing existing grants unless asked.
7. Report which metadata was updated, why, and what still needs verification.

## Guardrails

- Preserve org-specific customizations.
- Prefer additive changes.
- Start in `salesforce-metadata` when the user is primarily creating or changing schema, then hand off here for access follow-through.
- For demo-critical Lightning app shells, default to permission-set-first app visibility unless the project explicitly documents a different access pattern.
- Do not leave app visibility as a separate "later" follow-through task when the presenter path depends on a named Lightning app.
- Do not treat page visibility or field placement as proof that access is correct; verify object and field permissions explicitly.

## Routing Smoke Tests

Should trigger:
- `Update field visibility for the new sales operations fields.`
- `Add the permission-set grants for these new objects.`
- `Fix access to these fields for the support profile.`

Should not trigger:
- `Create a custom object and its fields for this process.`
- `Add a validation rule and page layout for this workflow.`

## Reference

- `.claude/skills/salesforce-metadata/SKILL.md`
- `.claude/skills/salesforce-metadata/reference.md`
