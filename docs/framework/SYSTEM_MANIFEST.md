# Engine System Manifest

Human-facing index of the Boilerplate-derived framework overlay in this fork. Scoped to engine development — customer/demo skills are intentionally absent.

## Skills

- `.claude/skills/salesforce-apex/`
- `.claude/skills/salesforce-metadata/`
- `.claude/skills/salesforce-deploy/`
- `.claude/skills/salesforce-flow/`
- `.claude/skills/field-level-security/`
- `.claude/skills/agentforce-dx/`
- `.claude/skills/agentforce-testing/`
- `.claude/skills/agentforce-observability/`
- `.claude/skills/open-salesforce-org-browser/`
- `.claude/skills/salesforce-ui-verification/`
- `.claude/skills/deslop/`
- `.claude/skills/diagnostic-refresh/`
- `.claude/skills/project-state-tracking/`
- `.claude/skills/red-team-review/`

## Claude Code Entry Points

- `CLAUDE.md` — engine-development AI context doc, auto-loaded by Claude Code
- `.claude/skills/<name>/SKILL.md` — natively discovered as `/<name>` slash commands
- `.claude/settings.json` — project-level permissions for the standard toolchain
- `.mcp.json` — MCP server entries for `salesforce-dx`, `firecrawl-heroku`, `sf-docs`

## Helper Agents

- `.claude/agents/salesforce-developer.md`
- `.claude/agents/tester-qa.md`

## What Is NOT In This Fork

This fork carries **only** engine-relevant Boilerplate skills. Intentionally absent:

- All customer/account scaffolding (`customer/`, account research)
- Demo lifecycle skills (`demo-lifecycle`, `demo-orchestration`, `demo-prep`, `demo-audit`, `solution-demo2win`, `requirements-tracking`)
- Discovery/research skills (`discovery-draper`, `company-research`, `popup-pitch`, `exec-ready-review`, `brainstorming`, `grill-me`, `poc-lifecycle`)
- Branding/Experience Cloud skills (`experience-cloud-branding`, `experience-cloud-lwr`, `salesforce-ux-designer`)
- External-tool skills (`notebooklm-workflows`, `slack-context`, `slack-personal-digest`, `linkedin-stakeholder-enrichment`, `gamma-authoring`, `lucid-diagram-architect`)
- Boilerplate maintenance (`boilerplate-maintenance`, `boilerplate-wrap-up`, `boilerplate-sf-skill-lab`, `agent-retro-review`)
- Sibling-rollout machinery (`scripts/sync_to_sibling.py`, `scripts/sync_lib.py`, `boilerplate-state.json`, `BOILERPLATE_VERSION`)

If a future engine-dev need surfaces that one of these skills would solve, copy it in deliberately rather than re-importing the full Boilerplate surface.

## Reference Docs

- `CLAUDE.md` — engine-dev context
- `docs/framework/README.md` — framework overview
- `docs/ENGINE_DEV_LOG.md` — engine-specific decisions, install-mechanism findings, license conversation status
- `README.md` — Dylan's original engine README (authoritative for engine functionality)
