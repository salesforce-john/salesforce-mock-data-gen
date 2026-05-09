# Agentforce DX Reference

## Scope

`agentforce-dx` owns Agentforce design, build, update, validation, and deployment for Boilerplate projects.

Use sibling skills when the request is mostly about:

- repeatable smoke or regression coverage -> `agentforce-testing`
- preview or post-deploy diagnosis -> `agentforce-observability`

## Routing Precedence

Use this routing split when prompts sit near demo work:

- `demo story`, `storyboard`, `talk track`, `tell-show-tell`, or `demo flow` -> demo skills
- `customer sandbox`, `pilot agent`, `POC agent`, `sandbox validation`, `sandbox handoff`, `CCR sizing`, or `adoption plan for live users` -> `agentforce-dx`
- `preview failure`, `trace analysis`, or `live behavior diagnosis` -> `agentforce-observability`
- `saved smoke`, `regression suite`, or `safety probes` -> `agentforce-testing`

When a request includes both demo and sandbox language, prefer `agentforce-dx` once it is clearly about post-demo customer validation or live-user readiness rather than presales storytelling.

## Authoring Stance

- Treat Agentforce work as an Agent Development Lifecycle (ADLC): design, develop, test and validate, deploy, then monitor and tune.
- Treat post-demo customer sandbox work as part of the same ADLC, not as an extension of demo orchestration.
- Default to Agent Builder and Agent Script as the primary modern authoring path.
- Keep legacy YAML artifacts under `specs/` when the existing project already uses them or when a handoff still depends on that surface.
- Use `docs/AGENTFORCE_REQUIREMENTS.md` as the default human-facing intake artifact when you need to capture role, jobs to be done, grounding, actions, guardrails, validation prompts, and success metrics before implementation.
- Do not force a single storage format to carry every requirement. Agent Builder instructions, Agent Script, backing logic, Flow, Apex, and permissions can all contribute to the final behavior.

## Customer Sandbox Mode

When the request is for a customer sandbox or early pilot:

- Frame the use case as either `technical discovery sandbox` or `limited pilot`.
- Favor high-impact, low-complexity, fast-time-to-value use cases.
- Avoid treating the SE as the owner of a full production implementation.
- Call out production-only requirements that are intentionally excluded from the sandbox scope.

Default handoff patterns:

- `Momentum Program` -> primary delivery owner is typically `FDE`
- `custom integrations or multicloud complexity` -> primary delivery owner is typically `Partner`
- `straightforward in-house team` -> primary delivery owner is typically `CSM` or the customer's internal team

Document supporting teams whenever the real ownership is shared.

## Document Ownership

Keep these source-of-truth boundaries explicit:

- `docs/AGENTFORCE_REQUIREMENTS.md` -> intake, design intent, scope, success metrics, CCR sizing inputs, adoption assumptions, and handoff decisioning
- `docs/AGENTFORCE_DX_CHECKLIST.md` -> operational verification steps and readiness gates
- `docs/AGENTFORCE_SANDBOX_HANDOFF.md` -> packaged transition artifact for delivery teams and customer operators

The checklist and handoff artifact should reference requirement fields rather than restating them in full.

## ADLC Phase Map

Use this phase map to keep Agentforce work separate from a traditional SDLC mindset:

1. `Ideation and Design`: clarify role, user journeys, grounding, actions, guardrails, and measurement.
2. `Development`: implement Builder configuration, Agent Script, actions, grounding, and supporting logic.
3. `Testing and Validation`: preview the changed path, adjacent path, guardrails, and handoffs; save suites when repetition matters.
4. `Deployment and Release`: deploy the relevant metadata, verify activation, and confirm downstream wiring.
5. `Monitoring and Tuning`: use traces, session evidence, escalation rates, and user outcomes to refine instructions, scripts, and backing logic.

You can also think in the operator-friendly loop often used in enterprise Agentforce rollouts:

- `Prototype and Review`
- `Build and Ground`
- `Validate and Harden`
- `Deploy and Orchestrate`
- `Monitor and Refine`

## Org Gate

- Treat Agentforce work as local-only until the project has a target org in `.sf/config.json` or `.sfdx/sfdx-config.json`, or the user explicitly provides an org alias.
- Before new org-backed Agentforce work, run `python scripts/check_org_readiness.py`.
- Use Salesforce MCP first for org-backed work. Fall back to `sf` CLI only when MCP coverage is missing or fails.

## Core Commands

- `sf agent generate agent-spec`
- `sf agent create`
- `sf agent preview`
- `sf org open agent`

Use CLI commands when they fit the current project surface or are needed for verification. Do not turn a Builder-first workflow into a CLI-first workflow unless the task or repo already depends on it.

## Preferred Build Path

For new or modernized work:

1. Capture the design in `docs/AGENTFORCE_REQUIREMENTS.md`.
2. Build the agent in Agent Builder with Agent Script or the current Builder authoring surface.
3. Reuse or add grounding and deterministic backing logic only where needed.
4. Validate in preview before deploy or activation.
5. Deploy and verify post-deploy wiring.
6. Return to monitoring and tuning based on real sessions.

For customer sandbox work, also:

7. Record the sandbox type, scope boundaries, adoption plan, and primary delivery owner before treating the pilot as ready for handoff.
8. Package the transition in `docs/AGENTFORCE_SANDBOX_HANDOFF.md` when the output is meant for the customer team, FDE, partner, or CSM.

## Legacy YAML Interop

When the project still uses YAML specs:

- Keep specs under `specs/`.
- Use 2-space indentation.
- Include `agentType`, `role`, `companyName`, and `companyDescription`.
- Make action input names and Apex method signatures match exactly.
- Treat YAML as a legacy or interoperability artifact, not the default modern design center.

## Concrete Authoring And Scaffold Ergonomics

When official Agentforce or Labs materials provide useful concrete examples, absorb them here before considering any new runtime route. The gap worth closing is usually operator ergonomics, not lifecycle doctrine.

Keep the example surface small and reusable:

1. Start from `docs/AGENTFORCE_REQUIREMENTS.md` and capture:
   - role and jobs to be done
   - grounding sources
   - actions and backing logic
   - guardrails and escalation paths
   - validation prompts and success metrics
2. Run the existing-logic scan before creating anything new.
3. When direct `.agent` authoring is in play, keep the structure explicit:
   - `system` instructions for behavior and safety framing
   - `config` for stable identity and developer-facing settings
   - `start_agent` plus topic structure for routing and orchestration
   - action references and grounding inputs that match real backing assets
4. If the workflow needs new Flow, Apex, prompt, or permission assets, call out the scaffold need and hand off to the owning skill instead of hiding the work inside Agentforce guidance.
5. If the improvement is mostly an example, snippet, or operator recipe, keep it in this reference surface rather than creating a parallel Agentforce skill.

## Existing Logic Scan

Before creating new backing logic:

1. Inspect the project for existing Apex invocables, Flows, prompt assets, knowledge, semantic-layer assets, Data Cloud grounding, or related metadata that already satisfy the need.
2. Reuse and document existing assets before creating new stubs.
3. Call out any gaps that still require manual Agent Builder wiring, additional grounding, or new backing logic.

## Data Cloud / Data 360 Grounding

For Data Cloud / Data 360 grounding work — **Retriever, Search Index, SDM, Calculated Insight, DLO, DMO, segment, activation, identity resolution** — the project-local `data360` MCP is the preferred tool. It exposes the full Data 360 Connect API (~190 endpoints) behind a `search` → `payload_examples` → `execute` facade and resolves auth from the project's default target org each launch. See [docs/D360_MCP_SETUP.md](../../../docs/D360_MCP_SETUP.md) for the one-time build and `python scripts/check_d360_mcp.py` for readiness validation. Subject to the same project-local target-org gate as Salesforce MCP.

## Public Docs Retrieval

For public Agentforce, Agent Builder, or Salesforce Help research:

1. Use the project-local **`sf-docs`** MCP for anything on `help.salesforce.com` or `developer.salesforce.com` — it is the default Salesforce-doc retrieval path. Validate with `python scripts/check_sf_docs_mcp.py`. See [docs/SF_DOCS_MCP_SETUP.md](../../../docs/SF_DOCS_MCP_SETUP.md) for the one-time clone + build.
2. Use **`firecrawl-heroku`** for non-Salesforce sources only — third-party blogs, partner sites, news, general web research. Do not use Firecrawl for Salesforce help/developer docs when sf-docs is healthy.
3. If a Help article is found only through a parent Help page, adjacent title, or external reference rather than a direct indexed article body, mark the result as lower confidence before turning it into durable repo guidance.
4. Prefer official Salesforce Help and developer docs over practitioner notes when promoting durable Agentforce workflow guidance.

## Behavior Versus Rule

Use this split whenever instructions start mixing UX guidance with business enforcement:

- `Behavior`: phrasing, clarification style, response sequencing, confirmation patterns, and topic-level guidance.
- `Rule`: must-enforce requirements implemented through deterministic logic, action gating, permissions, validation, handoffs, or other controls.

Do not assume every rule belongs in Agent Script alone.

## Preview Verification

Before publish or activation:

1. Verify the changed path in preview.
2. Verify at least one adjacent path that could regress because of the same change.
3. Verify at least one off-topic, ambiguous, or guardrail path when user-facing behavior changed.
4. Record what was validated so the user can see the actual coverage.
5. If the request becomes a saved smoke or regression suite, move that work to `agentforce-testing`.

## Deployment Order

1. Deploy and activate prompt templates, actions, and dependent backing logic
2. Create or update the agent through the surface the project uses
3. Activate the agent
4. Deploy dependent Flows or metadata
5. Verify any manual Agent Builder wiring, action bindings, and downstream orchestration

## Publish Gates

Do not publish or activate user-facing changes unless all of the following are true:

- the relevant source of truth is updated for the current project surface
- backing logic, grounding, and action signatures are aligned
- required validation passed
- preview evidence exists for the changed path plus one adjacent path
- any guardrail or handoff path needed for the change has been checked
- the user wants the deploy or publish step to proceed

## CCR Sizing

When sandbox work needs a credit estimate:

- Use the simple workload model: `annual interactions x average credits per interaction = estimated CCR`
- Treat the result as technical scoping guidance, not finance-grade forecasting
- Record the volume source, time range, owner, reasoning-depth assumptions, and confidence level
- Include efficiency notes such as context pruning, atomic actions, and latency watchpoints
- If the customer needs a long-range commercial model, hand that work to the AE or specialist owner rather than presenting it as SE-owned finance output

## Monitoring And Tuning

After deploy:

1. Review preview traces, session evidence, escalation patterns, or observability outputs when available.
2. Identify whether the next fix belongs in Builder instructions, Agent Script, grounding, backing logic, permissions, or deployment wiring.
3. Hand deeper preview or post-deploy diagnosis to `agentforce-observability` when the failure is no longer a straightforward build task.

## Troubleshooting

- Agent missing from Flow picklists: activate the agent, then reopen Flow Builder
- Metadata locked: deactivate, deploy, reactivate
- Actions missing after deploy: verify UI-only wiring in Agent Builder
- Preview issues: update CLI and confirm the agent plugin is installed
- Behavior drift after launch: treat it as a monitoring-and-tuning task, not proof that the original deploy was complete
