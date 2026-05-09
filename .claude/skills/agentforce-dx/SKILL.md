---
name: agentforce-dx
description: Guides Agentforce work across the Agent Development Lifecycle (ADLC), including post-demo customer sandbox builds and early pilots, defaulting to Agent Builder and Agent Script for modern authoring while preserving legacy YAML interoperability when needed. Use when building or modifying Agentforce agents, shaping lifecycle work, planning customer sandbox validation, verifying wiring, or deploying and activating agent changes. Use sibling skills for repeatable testing and trace-first diagnosis.
---
# Agentforce DX

## Workflow

1. Treat Agentforce work as ADLC, not traditional SDLC. Classify the request into the current phase or loop: design, development, testing and validation, deployment, or monitoring and tuning.
2. Separate presales demo asks from post-demo customer sandbox asks. If the request is about a customer sandbox, pilot, sandbox handoff, CCR sizing, or adoption planning for live users, keep it in `agentforce-dx` rather than demo workflows.
3. For customer sandbox work, frame the build as either a technical discovery sandbox or a limited pilot. Favor use cases with high business impact, low technical complexity, and fast time to value.
4. Default to Agent Builder and Agent Script for modern authoring. Keep YAML artifacts in `specs/` readable and maintainable when the project already uses them or when interoperability with legacy flows is required.
5. Start from an explicit design artifact. Use `docs/AGENTFORCE_REQUIREMENTS.md` to capture role, jobs to be done, grounding, actions, guardrails, validation prompts, success metrics, CCR sizing inputs, adoption assumptions, and handoff decisioning before implementing.
6. Treat document roles explicitly: `docs/AGENTFORCE_REQUIREMENTS.md` is the intake and design source of truth, `docs/AGENTFORCE_DX_CHECKLIST.md` owns operational readiness checks, and `docs/AGENTFORCE_SANDBOX_HANDOFF.md` packages the post-sandbox transition for delivery teams and customer operators.
7. Scan for reusable backing logic and grounding assets before creating new Apex, Flow, prompt, knowledge, Data Cloud, or semantic-layer assets. Prefer reuse over new stubs.
8. Separate conversational behavior from deterministic enforcement. Put flexible response guidance in agent instructions or Agent Script flow, and enforce hard business rules through backing logic, action gating, validation, permissions, or handoff controls.
9. When the implementation requires a concrete build surface, hand off explicitly:
   - `salesforce-metadata` for schema and supporting metadata
   - `salesforce-flow` for declarative actions or wrappers
   - `salesforce-apex` for invocable or code-backed logic
   - `salesforce-lwc` for UI support work outside Agent Builder authoring
   - `salesforce-deploy` for validation and rollout sequencing around non-Agentforce metadata
10. When researching public Salesforce Help content for Agentforce, use the Salesforce docs MCP path available in the workspace first (currently `user-mcp-adaptor` `doc_search` with `Webpages` weighting). Use Firecrawl only if the Help article does not resolve cleanly through the indexed docs corpus.
11. If a Help article is only indirectly discoverable by indexed title, parent page, or external reference, treat the result as lower confidence and say so before promoting it into durable guidance.
12. If no local target org is configured yet, stop at local design, script, and metadata preparation. Use org-backed Salesforce MCP or `sf` commands only after the project has a local target org or the user explicitly provides an org alias.
13. Before new org-backed Agentforce work in a target project, run `python scripts/check_org_readiness.py`.
14. Use Salesforce MCP first for org-backed inspection, deploy, and validation steps. Fall back to `sf agent` CLI only when MCP coverage is missing or fails under the same org preconditions.
15. Validate the changed path plus at least one adjacent path before publish or activation. Include one off-topic or guardrail case whenever user-facing behavior changed.
16. When customer sandbox work needs a credit estimate, keep it at technical-scoping fidelity: record the workload source, assumptions, and confidence level, but do not present it as a finance-grade CCR model.
17. When the request needs saved smoke coverage, broad simulations, or repeatable regression suites, hand that work to `agentforce-testing`. When the request is primarily about broken preview or live behavior, hand it to `agentforce-observability`.
18. During deploy or activation work, verify agent activation, Flow or UI wiring, action bindings, and any remaining Agent Builder-only configuration in the target org.
19. Treat production evidence as an input to the next iteration. Monitoring, tuning, and follow-up prompt or action changes are part of the same lifecycle, not out-of-band maintenance.

## Guardrails

- Do not treat a global default org as sufficient; require a project-local target org or explicit alias.
- Do not route customer sandbox, pilot, CCR, or sandbox handoff requests into demo skills once the request has moved beyond presales storytelling.
- Do not present a customer sandbox as a production implementation or assume the SE owns the long-term delivery program.
- Do not present CCR sizing as a CFO-grade forecast; treat it as technical scoping input with source notes and confidence.
- Do not present Agentforce as ship-and-forget; monitoring and refinement are expected parts of the workflow.
- Do not default to Firecrawl for public Salesforce Help articles when the Salesforce docs MCP can return the indexed Help content.
- Do not publish or activate user-facing changes without validation plus preview evidence for the affected paths.
- If the request is primarily "test this agent," route to `agentforce-testing`.
- If the request is primarily "why is preview/live behavior wrong," route to `agentforce-observability`.

## Reference

- For detailed command, wiring, and troubleshooting guidance, read [reference.md](reference.md).
