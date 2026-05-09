# Salesforce Metadata Reference

## Purpose

Use this reference when the ask starts in schema or admin metadata and you need a compact, reusable checklist that keeps follow-through explicit without creating a new runtime route.

This reference is intentionally breadth-first. It covers the common surfaces that often travel together:

- object and field changes
- validation-rule follow-through
- page layout or FlexiPage implications
- permission and access follow-through

## Compact-Core Checklist

### 1. Clarify the primary metadata change

Identify which of these is actually changing:

- object or field model
- record-type behavior
- validation logic
- page composition or field visibility on pages
- access model

Keep the change as small and additive as possible unless the user explicitly asked for cleanup or restructuring.

### 2. Confirm the source of truth

Start with the smallest local source that can answer the question:

- object and field XML
- layouts, record types, validation rules, or related metadata already in the repo
- org-backed inspection only when the project has a local target org or the user explicitly provides an org alias

### 3. Check validation-rule and automation follow-through

If the change touches required fields, formulas, record state, or save-time behavior:

- inspect existing validation rules before adding another one
- check whether Flow, Apex, or page behavior depends on the same fields
- prefer one clear validation boundary over overlapping rule layers

If the primary work becomes automation or code, hand off the implementation to `salesforce-flow` or `salesforce-apex` after the schema decisions are stable.

### 4. Check page-layout or FlexiPage implications

When object or field changes affect how users work:

- decide whether the page needs layout updates, Dynamic Forms updates, or FlexiPage follow-through
- call out when a field exists in schema but will still be invisible or awkward in the current UI
- when the work supports a Salesforce demo, call out the launch surface and whether the field, component, or page is actually placed where the presenter will use it
- keep page composition implications explicit even if the actual page build lands in another surface later

If the work becomes primarily Lightning page design or LWC surface design, hand off to the owning UI skill after the metadata contract is clear.

When a Salesforce demo scene depends on a Lightning app shell, define one deterministic app-shell bundle instead of leaving adjacent follow-through implicit:

- the named `CustomApplication`
- the landing or home `FlexiPage`
- the presenter permission set carrying `applicationVisibilities`
- any required tabs or adjacent access the opening path depends on
- the launcher path the connected presenter user will actually follow

### 5. Check permission and access follow-through

Schema work is not done when the XML exists.

For new or changed objects and fields, decide:

- which permission sets or profiles need object access
- which fields need read/edit visibility
- whether tab, app, or related visibility also needs follow-through
- whether a demo-critical app shell needs permission-set-first app visibility in the same pass

When the primary job becomes grants and visibility updates, hand off to `field-level-security`.

### 6. End with the downstream map

Before leaving the metadata task, report:

- metadata changed
- validation or automation implications
- page/layout or FlexiPage implications
- permission/access follow-through needed
- named Lightning app, landing page, presenter permission set, and launcher-path follow-through needed, when relevant
- demo launch-surface or placement follow-through needed, when relevant
- next owning skill, if any

## Example Triggers That Still Belong To `salesforce-metadata`

- `Add a custom object and the supporting fields for this workflow, then tell me what else needs follow-through.`
- `Create a validation rule for this stage transition and call out any page or access updates we should not forget.`
- `Inspect this object change and tell me the metadata, layout, and permission consequences before we build automation.`
