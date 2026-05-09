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

(none yet)
