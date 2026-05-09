# Boilerplate Framework

Boilerplate runs a single agent runtime: Claude Code. Cursor IDE remains the editor.

- `CLAUDE.md` at the project root: unified AI context doc (auto-loaded by Claude Code) — owns trigger routing, doctrine, and toolchain policy
- `.claude/skills/`: workflow playbooks, specialist procedures, and reusable task guidance. Each `<name>/SKILL.md` is natively discovered by Claude Code as a `/<name>` slash command.
- `.claude/agents/`: reusable runtime helper agents for bounded implementation, design, and QA lanes inside an owning workflow
- `docs/framework/`: human-facing reference material that should not stay in the runtime surface

## Capability-First Use Model

- Route by job-to-be-done and the next durable artifact, not by named roles.
- The Trigger Routing section of `CLAUDE.md` is the authoritative trigger router.
- When an ask spans multiple workflows, start with the first missing durable artifact and then hand off through existing skills.
- When work branches into independent implementation, UI, or QA lanes, use `.claude/agents/` as helper surfaces without replacing the owning route or skill.
- Durable working memory lives in project artifacts such as `docs/PROJECT_STATE.md`, `docs/DEMO_REQUIREMENTS.md`, `customer/{account}/_context.md`, dated customer notes/readbacks, and optional NotebookLM notebooks.
- During `demo-lifecycle`, use `docs/_demo_working/<demo-slug>-<YYYYMMDD-HHMM>/` as non-canonical run space while keeping `docs/DEMO_REQUIREMENTS.md` as the parent-owned demo truth.

## Project Skills

- Mission workflows: `constructive-mission`, `diagnostic-refresh`, `doctrine-retro`, `brainstorming`
- Account intelligence: `company-research` for durable company research, entity resolution, and public-company quarter analysis
- SE deliverables: `discovery-draper`, `demo-lifecycle`, `demo-audit`, `demo-orchestration`, `solution-demo2win`, `popup-pitch`, `gamma-authoring`, `exec-ready-review`
- Specialist operators: `project-state-tracking`, `requirements-tracking`, `field-level-security`, `salesforce-ux-designer`, `demo-prep`
- Salesforce UI proof: `salesforce-ui-verification` for App Launcher, landing-state, object-surface, and KPI plausibility verification with durable evidence bundles
- Experience Cloud workflows: `experience-cloud-branding` for branding and theming on existing sites, `experience-cloud-lwr` for Enhanced/LWR site structure, `DigitalExperienceBundle`, static asset pipeline, and republish-aware implementation
- Quality passes: `deslop`, `red-team-review` for adversarial plan critique and failure-mode analysis
- Agentforce lifecycle: `agentforce-dx` for ADLC design/build/deploy, post-demo customer sandbox planning, and handoff preparation with Agent Builder and Agent Script as the primary modern path, `agentforce-testing` for smoke/regression coverage, `agentforce-observability` for trace-first diagnosis and tuning
- Integrations: `notebooklm-workflows`, `slack-context`, `slack-personal-digest`, `linkedin-stakeholder-enrichment`
- Browser automation: `salesforce-ui-verification`, `open-salesforce-org-browser`

## Project Runtime Agents

- `salesforce-developer`: scoped Salesforce implementation plus bounded CLI validation once the build surface is known
- `ui-designer`: UX critique and concrete implementation guidance for Lightning, Flow, App Builder, and Experience Cloud work
- `tester-qa`: focused verification, bug reproduction, and failure isolation without taking fix ownership away from the implementing lane

These agents may be used proactively on medium+ tasks or invoked directly by name, but they remain helper lanes inside the owning workflow rather than alternate routers.

## Boilerplate-Only Operations

- `boilerplate-maintenance`: backports, sibling rollouts, copy-surface validation, and rollout reporting from the Boilerplate workspace
- `boilerplate-wrap-up`: closeout handoff for landing-ready Boilerplate maintenance passes
- `.claude/agents/agent-retro-reviewer.md`: Boilerplate-only transcript review helper agent
- `scripts/project_lifecycle.py`: Boilerplate-only lifecycle entry point for bootstrap, open, overview, and archive delegation
- `scripts/sync_to_sibling.py` / `scripts/sync_lib.py` / `manifests/`: manifest-driven sibling rollout engine with drift detection and project-prefix exclusion
- `docs/PROJECT_LIFECYCLE_OPERATOR.md`: execution contract for the lifecycle operator
- `docs/BOILERPLATE_MAINTENANCE_LOG.md`: human-facing Boilerplate history only, not a workflow source of truth

## Copy Surface

Use `BOILERPLATE.md` as the source of truth for what gets copied into new projects. Treat that as the bootstrap copy surface. The maintenance reference defines the rollout-managed surface and which copied artifacts become project-local after bootstrap, such as `docs/PROJECT_STATE.md`, `docs/DEMO_REQUIREMENTS.md`, and the per-run folders that later appear under `docs/_demo_working/`. Reusable skills, project-facing helper agents, docs, and scripts get copied into target projects; Boilerplate-only skills, agents, and operating utilities stay in Boilerplate. For Agentforce intake, the project-facing reference doc is `docs/AGENTFORCE_REQUIREMENTS.md`. For customer sandbox transition packaging, use `docs/AGENTFORCE_SANDBOX_HANDOFF.md`.

For shared operator guidance across project-local and user-level MCP setups, use `docs/MCP_CONNECTION_HEALTH.md`.
