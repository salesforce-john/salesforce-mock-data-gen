# Engine Development Log

Engine-specific decisions, ongoing notes, and outstanding follow-ups for this fork. Newest entries on top.

## Outstanding follow-ups

### License conversation with upstream
- **Status:** open
- **Why it matters:** `dylandersen/salesforce-mock-data-gen` has no license file. Until a license exists upstream, sending code-PRs back to Dylan's repo is legally murky. Issues are fine; PRs are not.
- **Next action:** reach out to Dylan to discuss a permissive license (MIT or Apache-2.0 likely fits). Until resolved, the contribute-back loop scopes to this fork's `main` only.

### Phase 0 — install-mechanism spike (CP-0)
- **Status:** open
- **Goal:** prove how engine code lands in a customer demo project. The fork has its own `force-app/main/default/` SFDX layout; a naive `git subtree add --prefix=force-app/mock-data-engine` produces a broken nested structure.
- **Candidates to evaluate (in order):**
  1. **Subtree with `git subtree split` + filtered prefix** — split engine's `force-app/main/default/` into a synthetic standalone tree, then add at the project's `force-app/main/default/genai/`.
  2. **Copy-and-namespace** — script-driven copy of engine `classes/`, `flows/`, `genAiPromptTemplates/` with project namespace prefix on each file. Loses subtree-pull, no SFDX-layout collision.
  3. **2GP unlocked package** — engine published as a package; customer projects depend via package install. Cleanest separation, requires DevHub package ownership.
- **Deliverable:** `docs/INSTALL_SPIKE.md` capturing the surviving mechanism, install command, update mechanics, and which files end up engine-owned vs project-owned.

## Decisions and notes

### 2026-05-09 — First deliberate divergence from upstream: RFP_Analysis removed

Removed two upstream-inherited components from the engine:

- `force-app/main/default/genAiPlugins/RFP_Analysis.genAiPlugin-meta.xml`
- `force-app/main/default/genAiFunctions/Launch_RFP_Analysis_Flow/` (entire dir, 3 files)

**Why:** these are an Agentforce Topic plugin and a function for analyzing uploaded RFP documents on Opportunity records — a different domain from mock data generation. The function references a `Launch_RFP_Analysis_Flow` Flow that is **not present in this repo**, so the components shipped as a half-broken plugin from upstream. Deploying them into a customer demo project would surface an unowned, non-functional Agentforce capability with no deployable Flow behind it.

**Implication:** this is the first deliberate divergence from `dylandersen/salesforce-mock-data-gen`. Future `git fetch upstream && git merge upstream/main` operations will try to bring these files back. When that happens, resolve in favor of our deletion (i.e., `git rm` them again as part of the merge resolution). Do not include this deletion in any upstream PR back to Dylan — the cleanup is fork-local opinion, not a defect.

Discovered during the install-mechanism spike (CP-0). The scoped engine manifest at `manifest/engine-package.xml` already excluded these components from deploys; this commit removes the dead source files to keep the engine surface honest.
