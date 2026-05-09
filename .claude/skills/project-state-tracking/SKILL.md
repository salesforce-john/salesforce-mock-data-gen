---
name: project-state-tracking
description: Maintains `docs/PROJECT_STATE.md` as the always-current project summary. Use when the user asks for project status, a slick sheet, current state, top priorities, blockers, or to update the living state doc after meaningful work.
---
# Project State Tracking

## Artifact

- `docs/PROJECT_STATE.md`

## Workflow

1. Read `docs/PROJECT_STATE.md` if it exists; create or normalize it around the shared section structure when needed.
2. Update the file only after meaningful work:
   - scope changed
   - status changed
   - risks changed
   - a major artifact or workflow was added
   - the top priorities changed
3. Keep the file short and summary-oriented.
4. Refresh these sections first:
   - `Last Updated`
   - `Current Scope`
   - `Current Build Status`
   - `Top Work Done`
   - `Top Work To Do`
   - `Blockers And Risks`
   - `Latest Important Decisions`
5. If `docs/DEMO_REQUIREMENTS.md` exists, summarize only the current posture here and point to that file under `Linked Deep-Dive Artifacts` instead of duplicating episode tables.
6. Base updates only on evidence from code, docs, org state, or explicit user direction.
7. Report the current status, top priorities, and blockers after updating.

## Guardrails

- Do not turn `docs/PROJECT_STATE.md` into a changelog or transcript dump.
- Do not invent progress or completion status.
- Prefer concise bullets over exhaustive history.
- If nothing material changed, avoid noisy rewrites; update only when the current summary would otherwise mislead.
- Keep secrets, credentials, and sensitive operational details out of the file.

## Related References

- `docs/PROJECT_STATE.md`
- `docs/DEMO_REQUIREMENTS.md`
- `.claude/skills/requirements-tracking/SKILL.md`
