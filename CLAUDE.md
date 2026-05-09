# Salesforce Mock Data Generator — Engine Development Workspace

This repo is a **fork** of [dylandersen/salesforce-mock-data-gen](https://github.com/dylandersen/salesforce-mock-data-gen), evolved as the canonical AI demo data generator engine for Salesforce Solution Engineer customer demos. The engine is consumed by customer demo projects via a `mock-data-engine` skill in the [Boilerplate](https://github.com/j-schneider_sfemu/Boilerplate) workspace.

This file is the AI context doc for engine-development sessions. It is **not** a Boilerplate sibling — it is a fork that *uses* a curated subset of Boilerplate skills. No customer scaffolding, no demo lifecycle routing, no sibling-rollout machinery.

---

## Repository Context

- **`origin`** → `salesforce-john/salesforce-mock-data-gen` (this fork)
- **`upstream`** → `dylandersen/salesforce-mock-data-gen` (Dylan's repo). Pull improvements with `git fetch upstream` and rebase or cherry-pick as needed.
- **Branch protection on `main`** — direct pushes are rejected. All work lands via PR. No required reviewers (solo).
- **Boilerplate framework overlay** lives in a single labeled commit (`chore: add Boilerplate SE framework overlay`). Keep that commit surgically separable when crafting upstream PRs to Dylan's repo: PRs to upstream should never include `CLAUDE.md`, `.claude/`, `docs/framework/`, `scripts/check_*.py`, or `.github/` overlay files.
- **License** — upstream has no license. Until that conversation with Dylan happens, do not send code-PRs upstream. Issues are fine.

---

## Org Context

- **Project-local target org required.** Org-backed Salesforce MCP and `sf` CLI work is allowed only when an org alias is configured locally (`.sf/config.json`, `.sfdx/sfdx-config.json`) or explicitly provided. Do not rely on a global default org.
- **Engine dev typically uses scratch orgs.** Spin one up via `sf org create scratch` against your DevHub for engine work; do not develop against a customer's org.
- **Org readiness checkpoint:** when the active/default org changes, run `python scripts/check_org_readiness.py` before deploy, query, or test work.
- **Primary timezone:** EST.

---

## Available Skills

Curated subset of Boilerplate skills, scoped to engine development. Native slash-commands.

**Build-depth:**
- `salesforce-apex` — Apex class/trigger/invocable/test work
- `salesforce-metadata` — schema, fields, layouts, validation rules
- `salesforce-deploy` — deploy validation, rollout sequencing, post-deploy verification
- `salesforce-flow` — declarative automation, screen/record-triggered/scheduled flows
- `field-level-security` — FLS, profile/permission-set updates after schema changes

**Agentforce:**
- `agentforce-dx` — agent build, validate, deploy, activate
- `agentforce-testing` — smoke, regression, safety probes
- `agentforce-observability` — trace-first diagnosis and refinement

**Org / UI proof:**
- `open-salesforce-org-browser` — open connected org in Cursor browser
- `salesforce-ui-verification` — Lightning UI proof, App Launcher, landing-state

**Hygiene:**
- `deslop` — clean up AI-assisted code changes before commit
- `diagnostic-refresh` — root-cause analysis when simple fixes fail
- `project-state-tracking` — maintains `docs/PROJECT_STATE.md` if used
- `red-team-review` — adversarial review for high-stakes design decisions

**Helper agents (under `.claude/agents/`):** `salesforce-developer`, `tester-qa`. Invoke directly by name on medium+ tasks when work splits into independent build and verification lanes.

---

## Toolchain

- **MCP:** `salesforce-dx`, `firecrawl-heroku`, `sf-docs`. Wired via `.mcp.json`. Salesforce DX MCP is bound to `DEFAULT_TARGET_ORG` — set a local target org first.
- **Salesforce help routing:** prefer `sf-docs` MCP for `help.salesforce.com` and `developer.salesforce.com`. Use `firecrawl-heroku` only for non-Salesforce web research.
- **`gh` CLI:** active account is `salesforce-john` for fork operations. Switch with `gh auth switch --user salesforce-john` before pushing or opening PRs.

---

## Engine Development Conventions

- **Goal of refactor work:** evolve toward an object-agnostic generator descriptor — see `docs/ENGINE_DEV_LOG.md` for ongoing decisions and findings.
- **Per-customer changes do not live here.** Customer demo projects consume this engine via the Boilerplate `mock-data-engine` skill and customize generators locally in their own repos. Engine improvements that come back from customer builds do so as sanitized GitHub Issues against this repo (default channel) or sanitized PRs against topic branches.
- **Do not include customer-identifying content in any commit, PR, branch name, or issue.** Topic-named only (`feature/parent-lookup-fallback`, never `customer/<name>`).
- **Upstream PRs:** if a change is generic enough to send to Dylan's `dylandersen/salesforce-mock-data-gen`, do it from a clean topic branch with no Boilerplate overlay files in the diff. License conversation must be resolved first.

---

## References

- `docs/framework/README.md` — framework overview (Boilerplate-derived, scoped to this fork)
- `docs/ENGINE_DEV_LOG.md` — engine-specific decisions and ongoing notes
- `README.md` — Dylan's original engine README, kept as authoritative engine-functionality docs
