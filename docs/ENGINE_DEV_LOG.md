# Engine Development Log

Engine-specific decisions, ongoing notes, and outstanding follow-ups for this fork. Newest entries on top.

## Outstanding follow-ups

### License conversation with upstream
- **Status:** open
- **Why it matters:** `dylandersen/salesforce-mock-data-gen` has no `LICENSE` file. With no license, GitHub's terms of service grant viewing and forking only — they do not grant explicit modify/redistribute/contribute-back rights. The fork itself is fine (forking is permitted), but distributing engine code into customer projects sits in a legal gray area, and sending PRs back to Dylan's repo lacks a defined contribution license on either side.
- **Stance:** strict. **No upstream PRs to `dylandersen/salesforce-mock-data-gen` and no upstream Issues until the license conversation is resolved.** The cost of waiting is small; the cost of an awkward upstream interaction is real.
- **Next action:** reach out to Dylan personally to discuss adding a permissive license (MIT or Apache-2.0 most common for Salesforce work). Five minutes of his time once he's convinced. After that, contributions flow in both directions cleanly.

### Candidate upstream contributions (pending license)
Track items here that are ready to send upstream once the license conversation completes.

- **Scoped engine deploy manifest** (`manifest/engine-package.xml`, commit `73b8471`) — Dylan's existing `manifest/package.xml` is generic boilerplate with `*` wildcards across types the engine doesn't even use. The scoped manifest is a real improvement; cherry-pickable as a clean upstream PR.
- **RFP_Analysis cleanup** (commit `031aec6`) — should be a GitHub Issue first ("noticed RFP_Analysis references a Flow that isn't in the repo, was it meant to be included?"), not a deletion PR. Dylan may have the missing Flow locally and just hasn't committed it. Let him decide what action to take.

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
