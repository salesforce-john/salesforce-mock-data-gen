# Engine install spike — findings and recommended recipe

**Status:** complete (CP-0 of the salesforce-mock-data-gen adoption plan)
**Date:** 2026-05-09
**Spike target:** SDGovernment sibling, real customer-project SFDX layout
**Spike org:** disposable demo org (alias `SDGovSPIKE`)
**Validated deployment ID:** `0Afg7000003nkrBCAQ` (25 components, 25/25 succeeded)

## Goal

Prove how the engine's deployable metadata (`force-app/main/default/`) lands in a customer demo project that has its own existing SFDX layout. The candidates evaluated were git subtree split + filtered prefix, copy-and-namespace, and 2GP unlocked package. **Subtree (Candidate A) survived; recommended.**

## Recommended install recipe (for use by the `mock-data-engine` skill in CP-3)

**Important:** the engine repo's deployable metadata lives at `force-app/main/default/`. We need to install **only that subdirectory** at the customer project's `force-app/main/default/`, not the whole engine repo (which also contains `CLAUDE.md`, `manifest/`, `scripts/`, etc.). Naive `git subtree add --prefix=force-app/main/default engine main --squash` pulls the engine's *root* into the customer's prefix and produces a broken structure. The correct recipe uses `git subtree split` to extract just the deployable subdirectory first, then `git subtree add` from that local split branch.

```bash
cd /path/to/customer-project
git remote add engine https://github.com/salesforce-john/salesforce-mock-data-gen.git
git fetch engine main

git subtree split --prefix=force-app/main/default refs/remotes/engine/main -b engine-deployable
git subtree add --prefix=force-app/main/default engine-deployable --squash
```

This produces three commits in the customer project: an initial split commit, a squashed engine-content commit, and a merge commit. The squashed commit carries the subtree-tracking footer (`git-subtree-dir: force-app/main/default` and `git-subtree-split: <engine-sha>`) that makes future `git subtree pull` work.

**Verified end-to-end on 2026-05-09** against a throwaway repo at `/tmp/subtree-recipe-test/` (since deleted): install command landed all 6 engine subdirectories (`classes/`, `flows/`, `flowDefinitions/`, `genAiFunctions/`, `genAiPlugins/`, `genAiPromptTemplates/`) at the correct paths under the customer's `force-app/main/default/`, with subtree metadata written.

### Future updates (after engine improvements upstream)

Same split-first pattern, then pull from the local split branch:

```bash
cd /path/to/customer-project
git fetch engine main

git subtree split --prefix=force-app/main/default refs/remotes/engine/main -b engine-deployable-update
git subtree pull --prefix=force-app/main/default . engine-deployable-update --squash
```

The `.` in the pull command refers to the local repo (where the split branch lives). This works only if the install used the same split-then-add pattern. **It does not work** if the install used a manual `git merge -s subtree` approach (no subtree-tracking metadata written). If a project somehow has a manual-merge-style install, future updates must continue using `git merge -s subtree -X subtree=force-app/main/default --squash --allow-unrelated-histories engine/main`. The `mock-data-engine` skill should detect this case and document the workaround.

**Verified end-to-end on 2026-05-09**: a marker file (`force-app/main/default/.engine-version`) was added to engine main via PR #6, then pulled into the throwaway repo via the split-then-pull pattern. Pull merged cleanly, marker file landed at the expected path.

If `git subtree pull` reports `Subtree is already at commit X`, the engine's `force-app/main/default/` had no new commits since the last pull (engine maintenance work outside that subdirectory — like manifest comment updates — does not flow into customer projects). This is expected behavior, not a failure.

## Deploy command (use the scoped manifest, not source-dir)

The engine's deployable surface is **25 components** across 6 metadata types. Use the scoped manifest, never `--source-dir force-app/main/default` (which would also try to deploy the customer project's own metadata).

```bash
sf project deploy validate --manifest "/path/to/engine-clone/manifest/engine-package.xml" --target-org <customer-org-alias>
sf project deploy start --manifest "/path/to/engine-clone/manifest/engine-package.xml" --target-org <customer-org-alias>
```

The manifest lives in the engine repo at `manifest/engine-package.xml`. Customer projects can either reference it from the engine clone path (single source of truth) or copy it locally (lower coupling, drift risk). Skill should reference engine path by default.

## Engine-owned vs project-owned files (after install)

| Path | Owner | Notes |
|------|-------|-------|
| `force-app/main/default/classes/{ContactGenerator,CaseGenerator,EmailCreatorFromAI,KnowledgeArticleGenerator,TaskEventGenerator}.cls` (+ `*Test.cls`, `*-meta.xml`) | engine | 10 files (5 classes + 5 tests). Tests excluded from deploy manifest. |
| `force-app/main/default/flows/{AI_Email_Generator,Case_Generator_Flow,Contact_Generator_Flow,Knowledge_Article_Generator_Flow,Task_Event_Generator_Flow}.flow-meta.xml` | engine | 5 files |
| `force-app/main/default/flowDefinitions/{same names}.flowDefinition-meta.xml` | engine | 5 files |
| `force-app/main/default/genAiFunctions/{AI_Email_Generator,Generate_Case_Data,Generate_Contact_Data,Generate_Knowledge_Article_Data,Generate_Task_Event_Data}/` | engine | 5 dirs (genAiFunction-meta.xml + input/output schemas) |
| `force-app/main/default/genAiPlugins/Mock_*.genAiPlugin-meta.xml` | engine | 5 files |
| `force-app/main/default/genAiPromptTemplates/*.genAiPromptTemplate-meta.xml` | engine | 6 files |
| Anything else under `force-app/main/default/` | project | Customer project's own metadata, untouched by engine subtree pulls |

**Customer-specific edits should never modify engine-owned files.** When a customer project needs a customized generator (e.g., for a custom object), the recommended pattern is:
1. Clone the engine class into a new project-namespaced class (e.g., `<Slug>_ContactGenerator.cls`).
2. Adapt the clone for the customer's data model.
3. Leave the original engine class untouched on disk; let it deploy as-is or exclude it from the customer's deploy manifest.

This pattern keeps `git subtree pull` clean — engine improvements continue flowing in without touching customer customizations.

## Real-world layout collision check (one observed case)

In the SDGovernment spike, both the engine and SDGov had a `force-app/main/default/genAiPlugins/` directory with files. The merge **preserved both** — engine's 5 `Mock_*.genAiPlugin-meta.xml` files added cleanly alongside SDGov's existing `p_16jKj000000CiZt_DemoPlaceholder.genAiPlugin-meta.xml`. No conflict because the file names differed.

**This means the real collision risk is name-collision at the file level, not directory-level.** Future customer projects must inspect their `genAiPlugins/`, `flows/`, `flowDefinitions/`, and `classes/` directories for naming conflicts with the engine's components (listed in the manifest above) before installing. The `mock-data-engine` skill should perform this check as a precondition.

## Why subtree (Candidate A) won

- **Layout-clean:** engine's `force-app/main/default/` content lands at customer's `force-app/main/default/`, no nesting weirdness, files at standard SFDX paths.
- **Trace-able:** lineage is preserved in commit metadata; you can inspect what came from engine vs project.
- **Update-able:** with the split-then-add install pattern, future engine updates flow in via `git subtree split` + `git subtree pull --squash` (two commands; see "Future updates" above). The pull operation handles the actual content transfer cleanly.
- **Reversible:** `git reset --hard <pre-install-commit>` returns to baseline cleanly.

Copy-and-namespace and 2GP unlocked package were not formally tried because Candidate A succeeded on first attempt. They remain documented in the plan as fallback options if subtree fails on a customer project with structural reasons (e.g., complex multi-package-directory `sfdx-project.json`).

## Merge conflict recovery (when `git subtree pull` fails)

Three failure modes are likely as engine and customer projects evolve. Each has a deterministic recovery, but they are not obvious from `git`'s default error messages.

### Scenario 1: Divergent histories (`refusing to merge unrelated histories`)

**Symptom:** `git subtree pull --prefix=force-app/main/default . engine-deployable-update --squash` exits with `fatal: refusing to merge unrelated histories`.

**Cause:** customer project was installed via the manual `git merge -s subtree` approach (no subtree-tracking metadata) or the install was wiped and reinstalled, breaking the subtree lineage.

**Recovery:** drop back to the manual-merge update path. The file outcome is equivalent; you just don't get to use `git subtree pull` going forward unless you reinstall.

```bash
cd /path/to/customer-project
git fetch engine main
git merge -s subtree -X subtree=force-app/main/default --squash --allow-unrelated-histories engine/main
git status
git commit -m "chore: subtree update from engine main (manual merge fallback)"
```

If you want to restore the friendlier `git subtree pull` flow, the only path is full reinstall: `git rm -rf force-app/main/default/<engine-prefixed-files>`, then re-run the documented install recipe. This is destructive — back up customer customizations first.

### Scenario 2: Engine deleted a file the customer project still has

**Symptom:** `git subtree pull` succeeds with conflicts, like `CONFLICT (modify/delete): force-app/main/default/genAiPlugins/SomeOldPlugin.genAiPlugin-meta.xml deleted in engine-deployable-update and modified in HEAD`.

**Cause:** the engine removed a file (e.g., the RFP_Analysis cleanup in PR #3 of this fork) but the customer project edited the same file before the deletion landed upstream.

**Recovery:** decide whether the engine's deletion or the customer's edit wins. For engine cleanups (the typical case), accept the deletion:

```bash
git rm force-app/main/default/genAiPlugins/SomeOldPlugin.genAiPlugin-meta.xml
git commit -m "chore: accept engine deletion of SomeOldPlugin (was customized locally)"
```

If the customer's edit was important, save it elsewhere first (e.g., `cp <file> /tmp/customer-edit.xml`) before `git rm`, then port the edit into a project-namespaced clone (`<Slug>_SomeOldPlugin.genAiPlugin-meta.xml`) that's owned by the project, not the engine.

### Scenario 3: Operator edited an engine file directly

**Symptom:** `git subtree pull` reports a content conflict like `CONFLICT (content): Merge conflict in force-app/main/default/classes/ContactGenerator.cls`.

**Cause:** customer project violated the "do not edit engine-owned files" discipline. The engine improved the file upstream; the customer also edited it locally.

**Recovery (preferred — preserve engine version, port customer edit out):**

```bash
git checkout --theirs force-app/main/default/classes/ContactGenerator.cls
git add force-app/main/default/classes/ContactGenerator.cls
git commit -m "chore: accept engine version of ContactGenerator; customer edit migrated to <Slug>_ContactGenerator"
```

Then create the project-namespaced clone with the customer's edit as part of the same PR.

**Recovery (last resort — keep customer version, lose engine improvement):**

```bash
git checkout --ours force-app/main/default/classes/ContactGenerator.cls
git add force-app/main/default/classes/ContactGenerator.cls
git commit -m "chore: keep local customizations to ContactGenerator (declines engine update)"
```

This sets up the file for a content-conflict on every future pull. Strongly prefer the migrate-out approach.

### Why these aren't fully verified

Scenarios 1–3 are recovery patterns drawn from documented `git subtree` behavior and merge-conflict resolution norms. Recovery commands have been validated for syntax and intent against `git merge`/`git checkout` documentation but were not reproduced end-to-end in throwaway repos during the spike (cost-benefit: each scenario takes time to reproduce, and the recovery commands are deterministic given correct git behavior). If a future operator hits a scenario the recovery section doesn't cover, that's an input to RT-C and a doc improvement.

## Caveats and known limits

1. **First-install must use `git subtree add`, not manual `git merge -s subtree`.** Spike used the manual approach for layout-shape testing and discovered that the manual approach doesn't write subtree-tracking metadata, breaking `git subtree pull --squash`. SDGov was reset to baseline post-spike; the real install in CP-5b will use `git subtree add`.

2. **Install idempotency contract for the `mock-data-engine` skill.** The customer project must not already have an engine install elsewhere in the tree. The skill detects existing install via this rule:

   - **Trigger:** any of `force-app/main/default/classes/{ContactGenerator,CaseGenerator,EmailCreatorFromAI,KnowledgeArticleGenerator,TaskEventGenerator}.cls` exists in the customer project.
   - **Action on detection:** halt with a clear message (`Engine appears already installed at force-app/main/default/classes/<file>.cls. Skip-with-message; if reinstall is intended, remove existing engine files and rerun.`). Do not attempt to re-run `git subtree add` or `git subtree pull`.
   - **Edge case — partial install:** if *some but not all* generator classes exist, treat as detected (halt). The operator must reconcile manually before the skill can proceed; auto-merging a partial install with engine main risks silent overwrites of customer customizations.
   - **Why file-presence over hash-match:** hash-matching against current engine main creates false negatives when the engine evolves (a legit prior install becomes "out of date" and trips reinstall). File presence is a stable signal of "this project owns engine code"; the *update* path (subtree pull) is the right way to refresh, not reinstall.
   - **What "skip-with-message" means in the skill:** the workflow does not advance past the install step. Operator chooses one of three documented recovery paths below.

   **Reconciliation recipes (when the skill halts on detection):**

   The operator's choice depends on the *shape* of the existing install. The skill should ask which case applies before proceeding.

   - **Case A — full install, want to update.** All five generator classes present and the squash commit carries subtree-tracking metadata (check with `git log --grep='git-subtree-dir' force-app/main/default/`). This is a healthy install; the operator wanted "update" not "install." Skill routes to the future-updates flow (`git subtree split` + `git subtree pull --squash`) instead. No destructive action.

   - **Case B — full install, no subtree metadata** (manual-merge install, e.g. SDGov's spike approach). All five classes present but `git log --grep='git-subtree-dir'` is empty. Skill cannot use `git subtree pull` here. Two sub-paths:
     - **B.1 (preferred): switch to manual-merge updates.** Use the Scenario 1 recovery in the *Merge conflict recovery* section above. Acknowledges the install shape and uses `git merge -s subtree` for all future updates.
     - **B.2 (only if friendly pulls are required): destructive reinstall.** Back up customer customizations to `/tmp/<project>-customizations/` first (any project-namespaced classes, customer prompt template edits, anything outside engine-prefixed paths). Then `git rm` engine-prefixed files (the manifest is the inventory), commit, and re-run the documented split-then-add install. Restore customizations as a separate follow-up commit.

   - **Case C — partial install** (1–4 generator classes present, or generator classes present but `genAiPlugins/Mock_*.genAiPlugin-meta.xml` missing, or any other shape that doesn't match a clean install). Skill cannot proceed safely. Operator triages:
     - **Were the existing classes hand-copied by an SE pre-skill?** Migrate them to project-namespaced clones first (e.g., rename `ContactGenerator.cls` → `<Slug>_ContactGenerator.cls`, update all internal references). Then run the full install fresh. The original customer-edit lives in the namespaced clone; the engine's `ContactGenerator.cls` lands clean.
     - **Were the existing classes a partial subtree pull that errored?** Inspect `git log` for prior subtree commits. If found, treat as Case B. If not, treat as hand-copy (above).
     - **Don't know how they got there?** Run `git log --follow force-app/main/default/classes/ContactGenerator.cls` to find the introducing commit. Look at the commit message and author; ask the SE who made it. Do not auto-resolve.

   - **Case D — engine-prefixed files present in source but no commits in `git log` reference them** (e.g., files were copy-pasted into the working tree but never committed). Skill should detect this via `git ls-files force-app/main/default/classes/ | grep -E '(Contact|Case|Email|Knowledge|TaskEvent)Generator\.cls'` returning empty while the disk has the files. Halt with a different message (`engine-prefixed files exist on disk but are uncommitted; commit or remove before installing`). Forces the operator into a consistent state before the skill proceeds.

   The `mock-data-engine` skill's CP-3 implementation should encode these cases in its precondition check, with clear branching messages for each.

3. **`git subtree pull` will surface upstream divergences as merge conflicts.** Example: PR #3 in this fork removed `RFP_Analysis.genAiPlugin-meta.xml` and `Launch_RFP_Analysis_Flow/` (orphan capability). If a customer project somehow has those files locally (e.g., from a prior subtree pull when they existed upstream), the next `git subtree pull` will delete them — which is correct, but worth knowing. Conversely, if upstream Dylan ever adds files this fork doesn't want, customer projects pulling from upstream Dylan instead of this fork would import unwanted files. **The fork's `main` is the source of truth for customer projects, never `dylandersen/salesforce-mock-data-gen` directly.**

4. **License posture is unresolved.** Dylan's upstream repo has no `LICENSE` file. The `mock-data-engine` skill's strict stance (per `docs/ENGINE_DEV_LOG.md`): no upstream PRs and no upstream Issues to `dylandersen/salesforce-mock-data-gen` until the license conversation completes. This does not affect customer-project consumption of this fork.

5. **The scoped manifest may need updating** if upstream adds or removes generators. When that happens, update `manifest/engine-package.xml` in the same commit as the source change, or the manifest will go stale. CI invariants do not currently check manifest-vs-source consistency; this is operator discipline.

## Files produced by this spike

- `manifest/engine-package.xml` (PR #2, commit `73b8471`) — scoped 25-component deploy manifest
- RFP_Analysis cleanup (PR #3, commit `031aec6`) — removed `force-app/main/default/genAiPlugins/RFP_Analysis.genAiPlugin-meta.xml` and `force-app/main/default/genAiFunctions/Launch_RFP_Analysis_Flow/`
- `docs/ENGINE_DEV_LOG.md` updates (PR #4) — license stance and upstream-PR-candidate tracking
- This document (`docs/INSTALL_SPIKE.md`) — install recipe and findings for downstream consumers and RT-A reviewers

## Status going into RT-A

CP-0 verification items:
- [x] One-pager exists and names the surviving install mechanism
- [x] Spike branch was disposable; SDGov reset to baseline (`66cee46`) post-spike
- [x] Verified cycle: install on disposable branch, deploy to disposable org (`SDGovSPIKE`), 25/25 components validated against deployment ID `0Afg7000003nkrBCAQ`
- [x] **Recommended recipe verified end-to-end against a throwaway repo** (RT-A finding #1 closed). Install via split-then-add: marker file `force-app/main/default/.engine-version` (PR #6) was added to engine main, then pulled into the throwaway repo; pull merged cleanly with subtree-tracking metadata preserved. Throwaway repo at `/tmp/subtree-recipe-test/` deleted post-test.
- [x] Disposable demo org (`SDGovSPIKE`) noted; will not be used for customer demos
- [x] Surviving mechanism documented (commands, manifest, file ownership table)
- [x] Merge-conflict recovery commands documented for three likely failure modes (RT-A finding #2 closed). Recovery commands documented from `git subtree`/`git merge` behavior; not all reproduced in throwaway repos.
- [x] Idempotency contract for the `mock-data-engine` skill specified concretely (RT-A finding #3 closed): file-presence check on five generator classes, halt-with-message on detection, partial-install treated as detected.
- [x] **Surviving mechanism NOT yet committed to SDGov's working branch** — spike uncovered that the manual-merge approach used originally does not produce subtree-tracking metadata. The proper install (split-then-add) will happen in CP-5b via the `mock-data-engine` skill, not pre-loaded by the spike. SDGov decoupled from `SDGovSPIKE` and reconnected to its real demo org, ready for CP-5b.

The last item is a **deliberate divergence from the original plan wording**, which assumed the spike's surviving install would land directly on SDGov's working branch. Reason: the spike used `git merge -s subtree` for layout testing, but the recommended customer-project install is the split-then-add pattern. Re-doing the install via the proper commands, via the proper skill workflow, in CP-5b is cleaner than persisting a wrong-shape install.

Findings #4 (untested 2GP / copy-and-namespace fallbacks; multi-package-directory layout) and #5 (no enforcement of engine-file edit discipline) from RT-A are deferred to ENGINE_DEV_LOG as known limits; revisit if a customer project hits them.
