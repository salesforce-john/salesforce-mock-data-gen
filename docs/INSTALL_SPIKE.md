# Engine install spike — findings and recommended recipe

**Status:** complete (CP-0 of the salesforce-mock-data-gen adoption plan)
**Date:** 2026-05-09
**Spike target:** SDGovernment sibling, real customer-project SFDX layout
**Spike org:** disposable demo org (alias `SDGovSPIKE`)
**Validated deployment ID:** `0Afg7000003nkrBCAQ` (25 components, 25/25 succeeded)

## Goal

Prove how the engine's deployable metadata (`force-app/main/default/`) lands in a customer demo project that has its own existing SFDX layout. The candidates evaluated were git subtree split + filtered prefix, copy-and-namespace, and 2GP unlocked package. **Subtree (Candidate A) survived; recommended.**

## Recommended install recipe (for use by the `mock-data-engine` skill in CP-3)

For future customer projects, install the engine using `git subtree add` (cleaner than the manual-merge approach used during this spike):

```bash
cd /path/to/customer-project
git remote add engine https://github.com/salesforce-john/salesforce-mock-data-gen.git
git fetch engine main
git subtree add --prefix=force-app/main/default engine main --squash
```

This produces a single squash commit with the engine's `force-app/main/default/` contents merged into the customer project's `force-app/main/default/`. `git subtree add` writes subtree-tracking metadata to the commit, which makes future updates work via the friendly `git subtree pull` command.

### Future updates (after engine improvements upstream)

```bash
cd /path/to/customer-project
git fetch engine main
git subtree pull --prefix=force-app/main/default engine main --squash
```

This works only if the install used `git subtree add`. **It does not work** if the install used a manual `git merge -s subtree` approach (no subtree-tracking metadata written). If a project somehow has a manual-merge-style install, future updates must continue using `git merge -s subtree -X subtree=force-app/main/default --squash --allow-unrelated-histories engine/main`. The `mock-data-engine` skill should detect this case and document the workaround.

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
- **Update-able:** with `git subtree add`, future engine updates flow in via `git subtree pull --squash`. Single command.
- **Reversible:** `git reset --hard <pre-install-commit>` returns to baseline cleanly.

Copy-and-namespace and 2GP unlocked package were not formally tried because Candidate A succeeded on first attempt. They remain documented in the plan as fallback options if subtree fails on a customer project with structural reasons (e.g., complex multi-package-directory `sfdx-project.json`).

## Caveats and known limits

1. **First-install must use `git subtree add`, not manual `git merge -s subtree`.** Spike used the manual approach for layout-shape testing and discovered that the manual approach doesn't write subtree-tracking metadata, breaking `git subtree pull --squash`. SDGov was reset to baseline post-spike; the real install in CP-5b will use `git subtree add`.

2. **The customer project must not already have an engine install elsewhere in the tree.** The skill's idempotency check (CP-3 requirement) needs to detect existing engine code at `force-app/main/default/classes/{ContactGenerator,CaseGenerator,...}.cls` and skip-with-message rather than re-installing.

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
- [x] Verified cycle: install on disposable branch, deploy to disposable org (`SDGovSPIKE`), 25/25 components validated
- [x] Disposable demo org noted; will not be used for customer demos
- [x] Surviving mechanism documented (commands, manifest, file ownership table)
- [x] **Surviving mechanism NOT yet committed to SDGov's working branch** — spike uncovered that the manual-merge approach used here does not produce subtree-tracking metadata; the proper install (`git subtree add`) will happen in CP-5b via the `mock-data-engine` skill, not pre-loaded by the spike. SDGov is decoupled from `SDGovSPIKE` and reconnected to its real demo org, ready for CP-5b.

This last item is a **deliberate divergence from the original plan wording**, which assumed the spike's surviving install would land directly on SDGov's working branch. Reason: the spike used `git merge -s subtree` for layout testing, but the recommended customer-project install is `git subtree add`. Re-doing the install via the proper command, via the proper skill workflow, in CP-5b is cleaner than persisting a wrong-shape install for weeks.

RT-A should challenge this divergence among other things; the trade-off is documented and reversible.
