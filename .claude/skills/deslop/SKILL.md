---
name: deslop
description: Clean up AI-assisted code changes by removing defensive noise, style drift, and other low-value generated patterns. Use after implementation, before commit, or when the user asks to clean up generated code or remove AI slop.
---
# Deslop

## Workflow

1. Identify the exact scope to review: current diff, edited files, or a user-named file set.
2. Inspect for low-value generated patterns:
   - comments that do not match local style
   - defensive checks or try/catch blocks that are abnormal for trusted codepaths
   - casts to `any` or similar escape hatches added just to silence type issues
   - style inconsistencies introduced by generation rather than project convention
3. Remove only the slop. Preserve legitimate logic, safety checks, and user-authored intent.
4. Re-run the smallest useful verification step for the touched area.
5. Report what changed and any residual risks.

## Guardrails

- Never assume `git diff main...HEAD` is available; use the actual edited scope in this workspace.
- Never revert unrelated user changes.
- If a pattern might be intentional, leave it or ask.
- Treat this as a cleanup pass, not a license to refactor broadly.
