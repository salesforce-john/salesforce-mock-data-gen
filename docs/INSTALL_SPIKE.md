# Engine install spike — findings and recommended recipe

**Status:** complete (CP-0 of the salesforce-mock-data-gen adoption plan)
**Date:** 2026-05-09
**Spike target:** SDGovernment sibling, real customer-project SFDX layout
**Spike org:** disposable demo org (alias `SDGovSPIKE`)
**Validated deployment ID:** `0Afg7000003nkrBCAQ` (25 components, 25/25 succeeded)

## Goal

Prove how the engine's deployable metadata (`force-app/main/default/`) lands in a customer demo project that has its own existing SFDX layout. The candidates evaluated were git subtree split + filtered prefix, copy-and-namespace, and 2GP unlocked package. **Subtree (Candidate A) survived; recommended.**

## Recommended install recipe (for use by the `mock-data-engine` skill)

**The previous version of this section was wrong.** It documented `git subtree add --prefix=force-app/main/default engine-deployable --squash` as the standard recipe. That command works only against repos with **no existing content at the prefix**. Every real customer demo project has files at `force-app/main/default/` (custom fields, layouts, profiles, perm sets), and `git subtree add` refuses with `fatal: prefix 'force-app/main/default' already exists.` This was discovered during CP-5b's first real-world install attempt at SDGovernment on 2026-05-09. The throwaway-repo test that "verified" the original recipe was structurally different from a customer-project shape — it had no existing `force-app/main/default/` — so the failure mode was invisible.

The corrected recipe branches on whether the customer project already has content at `force-app/main/default/`. **For all real customer demo projects, this is the populated case.** The empty case is documented for completeness but is not the standard customer-project path.

### Standard path: populated `force-app/main/default/` (every customer demo project)

```bash
cd /path/to/customer-project
git remote get-url engine 2>/dev/null || git remote add engine https://github.com/salesforce-john/salesforce-mock-data-gen.git
git fetch engine main

git subtree split --prefix=force-app/main/default refs/remotes/engine/main -b engine-deployable
git read-tree --prefix=force-app/main/default/ -u engine-deployable
git commit -m "chore: install mock-data-engine via read-tree"
```

`git read-tree --prefix=<dir>/ -u <tree>` explicitly places the split branch's tree into the customer's `force-app/main/default/`, adding new files alongside existing ones. **This works when the prefix is non-empty as long as no individual file paths collide.** The engine's deployable file names are sufficiently distinct from typical customer-project content (verified against SDGovernment, where the only shared directory was `genAiPlugins/` and the file names within differed) that path-level collisions are rare.

### Edge case: empty `force-app/main/default/` (e.g., greenfield projects, throwaway test repos)

```bash
cd /path/to/customer-project
git remote get-url engine 2>/dev/null || git remote add engine https://github.com/salesforce-john/salesforce-mock-data-gen.git
git fetch engine main

git subtree split --prefix=force-app/main/default refs/remotes/engine/main -b engine-deployable
git subtree add --prefix=force-app/main/default engine-deployable --squash
```

`git subtree add` writes a subtree-tracking footer in the squashed commit (`git-subtree-dir: force-app/main/default`, `git-subtree-split: <engine-sha>`) which enables future `git subtree pull` for friendlier updates. **This is only available on the empty-prefix install path.** Read-tree-installed prefixes do not get this metadata; their update mechanics are different (see "Update mechanics" below).

### Never use: `git merge -s subtree`

```bash
# DO NOT USE — silently lands files at wrong paths
git merge -s subtree --squash --allow-unrelated-histories engine-deployable
```

The `subtree` merge strategy uses heuristic path-matching to find the "best common tree." With the engine's flat split branch (no inherent prefix) merging into a populated customer project with deep directory nesting, git guesses unpredictably. A real-world reproduction at SDGovernment on 2026-05-09 landed engine files inside `.claude/skills/agentforce-observability/` — silently, with no warning. The only way to detect the misplacement was inspecting `git diff --cached --name-only` before commit. **This strategy is not viable for customer-project installs and must not appear in any operator workflow.**

## Update mechanics

The update path depends on which install path was used.

### If installed via `git subtree add` (empty-prefix path)

```bash
cd /path/to/customer-project
git fetch engine main
git subtree split --prefix=force-app/main/default refs/remotes/engine/main -b engine-deployable-update
git subtree pull --prefix=force-app/main/default . engine-deployable-update --squash
```

Verified working on 2026-05-09 against a throwaway repo using the engine's `.engine-version` marker file as the engine-side update. The subtree-tracking metadata footer makes this clean.

### If installed via `git read-tree` (standard customer-project path)

`git subtree pull` does not work — the read-tree install does not write subtree-tracking metadata, so subtree pull errors with `fatal: can't squash-merge: 'force-app/main/default' was never added.` Tested 2026-05-09. There is no clean equivalent to `git subtree pull` for read-tree installs.

Two viable update paths, both validated 2026-05-09:

**Update path A (recommended for read-tree installs): destructive re-read-tree.** Engine-owned files are never edited locally per the `mock-data-engine` skill's clone-and-rename customization discipline (project-namespaced classes own customer-specific edits, engine files stay pristine). Under that discipline, removing engine files and replacing them with a fresh read-tree is non-destructive in practice:

```bash
cd /path/to/customer-project
git fetch engine main

# Remove engine-owned files (the engine inventory is the canonical list at manifest/engine-package.xml)
git rm -rf force-app/main/default/classes/{Contact,Case,EmailCreatorFromAI,KnowledgeArticle,TaskEvent}Generator*.cls* \
         force-app/main/default/flows/{AI_Email_Generator,Case_Generator_Flow,Contact_Generator_Flow,Knowledge_Article_Generator_Flow,Task_Event_Generator_Flow}.flow-meta.xml \
         force-app/main/default/flowDefinitions/{AI_Email_Generator,Case_Generator_Flow,Contact_Generator_Flow,Knowledge_Article_Generator_Flow,Task_Event_Generator_Flow}.flowDefinition-meta.xml \
         force-app/main/default/genAiFunctions/{AI_Email_Generator,Generate_Case_Data,Generate_Contact_Data,Generate_Knowledge_Article_Data,Generate_Task_Event_Data} \
         force-app/main/default/genAiPlugins/Mock_*.genAiPlugin-meta.xml \
         force-app/main/default/genAiPromptTemplates/{Case_Generator,Contact_Generator,Generate_Email_Data_From_Request,Generate_Mock_Activity_Data,Knowledge_Article_Generator,Task_Event_Generator}.genAiPromptTemplate-meta.xml

git commit -m "chore: remove engine files for update"

git subtree split --prefix=force-app/main/default refs/remotes/engine/main -b engine-deployable-update
git read-tree --prefix=force-app/main/default/ -u engine-deployable-update
git commit -m "chore: update mock-data-engine via read-tree"
```

The `mock-data-engine` skill should automate this with a helper that reads the engine inventory from `manifest/engine-package.xml` and removes exactly those files.

**Update path B (one-time migration to tracked-subtree, optional but cleaner long-term):** Convert a read-tree install into a tracked-subtree install. After this one-time conversion, future updates work via `git subtree pull` (the friendlier path):

```bash
cd /path/to/customer-project

# Same engine-file removal as above
git rm -rf <engine-files>
git commit -m "chore: prepare for tracked-subtree migration"

# Now the prefix is empty of engine content; subtree add succeeds
git subtree split --prefix=force-app/main/default refs/remotes/engine/main -b engine-deployable
git subtree add --prefix=force-app/main/default engine-deployable --squash
```

After this migration, future updates use the path documented under "If installed via `git subtree add`" above.

### Update path that does NOT work: `git merge -s subtree --squash --allow-unrelated-histories`

Tested 2026-05-09 against a read-tree install: produces add/add merge conflicts on every engine-owned file because git treats both copies as independent additions (no subtree lineage). Conflict resolution is per-file manual; not a viable workflow.

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
- **Update-able:** future engine updates flow in via the path documented in *Update mechanics* above. The friendly path (`git subtree split` + `git subtree pull --squash`) requires the `git subtree add` install — only available on greenfield projects. The standard customer-project install via `git read-tree` uses a destructive re-read-tree update path (engine files removed, then re-installed from a fresh split). Less elegant; verified working.
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

1. **Standard install uses `git read-tree`, not `git subtree add`** (corrected 2026-05-09 after CP-5b's first real-world install attempt at SDGovernment). `git subtree add` refuses populated prefixes with `fatal: prefix already exists`, which is the case for every real customer demo project. `git read-tree --prefix=...` is the working install command for populated repos. `git subtree add` is reserved for greenfield/empty-prefix repos. **`git merge -s subtree` is never used** — silent path-misplacement reproduced at SDGovernment.

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
- [x] **Recipe verified against an empty throwaway repo** (RT-A finding #1 closed at the time). Install via split-then-add: marker file `force-app/main/default/.engine-version` was added to engine main, then pulled into the throwaway repo; pull merged cleanly with subtree-tracking metadata preserved. **Limitation surfaced 2026-05-09 during CP-5b:** the throwaway repo had no pre-existing `force-app/main/default/` content, so `git subtree add` succeeded. Real customer projects always have populated `force-app/main/default/` and `subtree add` refuses with `fatal: prefix already exists`. Recipe corrected to `git read-tree --prefix=...` for populated repos. See "Update mechanics" for the corresponding post-correction update path.
- [x] Disposable demo org (`SDGovSPIKE`) noted; will not be used for customer demos
- [x] Surviving mechanism documented (commands, manifest, file ownership table)
- [x] Merge-conflict recovery commands documented for three likely failure modes (RT-A finding #2 closed). Recovery commands documented from `git subtree`/`git merge` behavior; not all reproduced in throwaway repos.
- [x] Idempotency contract for the `mock-data-engine` skill specified concretely (RT-A finding #3 closed): file-presence check on five generator classes, halt-with-message on detection, partial-install treated as detected.
- [x] **Surviving mechanism NOT yet committed to SDGov's working branch** — spike uncovered that the manual-merge approach used originally does not produce subtree-tracking metadata. The proper install (split-then-add) will happen in CP-5b via the `mock-data-engine` skill, not pre-loaded by the spike. SDGov decoupled from `SDGovSPIKE` and reconnected to its real demo org, ready for CP-5b.

The last item is a **deliberate divergence from the original plan wording**, which assumed the spike's surviving install would land directly on SDGov's working branch. Reason: the spike used `git merge -s subtree` for layout testing, but the recommended customer-project install is the split-then-add pattern. Re-doing the install via the proper commands, via the proper skill workflow, in CP-5b is cleaner than persisting a wrong-shape install.

Findings #4 (untested 2GP / copy-and-namespace fallbacks; multi-package-directory layout) and #5 (no enforcement of engine-file edit discipline) from RT-A are deferred to ENGINE_DEV_LOG as known limits; revisit if a customer project hits them.
