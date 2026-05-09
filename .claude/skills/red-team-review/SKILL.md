---
name: red-team-review
description: Stress-tests plans, proposals, and execution approaches by identifying failure modes, weak assumptions, evidence gaps, and dependency risk. Use when the user asks for a red team review, adversarial review, to challenge a plan, or when a high-stakes plan needs a brief skeptical pass before finalizing.
---
# Red Team Review

## Input Contract

- Review a concrete artifact, not a vague idea: plan file, written approach, draft requirements, or proposed workflow.
- Read the minimum adjacent repo context needed to test the artifact.
- If the artifact is too underspecified for a real adversarial pass, say so directly and name the missing inputs.
- Label each major challenge as `evidenced`, `inferred`, or `unverified`.

## Workflow

1. Confirm the artifact being reviewed and the decision it is trying to support.
2. Read only the nearby rules, skills, docs, or implementation surfaces that the artifact depends on.
3. Separate supported claims from inferred claims and open questions.
4. Identify the smallest set of failure modes most likely to break the plan.
5. Focus on unsupported assumptions, missing evidence, dependency order, security or permissions blind spots, reversibility, and stakeholder objection risk.
6. Decide whether the artifact is strong enough to proceed, revise, or block.
7. Escalate to a reviewer subagent only when the artifact is high-stakes, cross-functional, or still ambiguous after the first pass.

## Output

Use this structure:

```markdown
## Findings
1. `[severity]` Short statement of the risk or failure mode.

## Assumptions
- State any assumptions that materially affect the review.

## Short Summary
- Verdict: `proceed`, `revise`, or `block`
- What to change before proceeding
```

Guidance:
- Lead with the most likely failure modes, not stylistic polish.
- Prefer 1-4 high-signal findings over exhaustive lists.
- Tie each finding to evidence or explicitly label it as inferred or unverified.
- If an existing workflow already performed a meaningful skeptical audit, avoid repeating it unless deeper critique is needed.

## Routing Smoke Tests

Should trigger:
- `Give this implementation plan a red team review before we execute it.`
- `Stress test this demo plan and tell me the most likely failure modes.`
- `Challenge this approach and tell me what would break first.`

Should not trigger:
- `Give this draft an executive-ready review.`
- `Review this code change.`
- `Improve this skill description.`
- `Create a Cursor skill for extracting text from PDFs.`
