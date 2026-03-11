---
name: implementation
description: "Pick the next unchecked story from an implementation plan, implement it following the linked spec, verify builds and tests pass, then commit and push. Pass --straight-to-master to skip feature branches."
user_invocable: true
---

# Implementation Skill

Execute the next story from an implementation plan. Reads the plan, identifies the first unchecked item, follows the linked spec to implement the code, verifies builds and tests, then commits and pushes.

## Argument Handling

```
/implementation <path/to/IMPLEMENTATION-PLAN.md> [--straight-to-master]
```

- **First argument** (required): Absolute path to the `IMPLEMENTATION-PLAN.md` file.
- **`--straight-to-master` flag** (optional): When present, commits and pushes directly to the current branch (main/master). When omitted, creates a feature branch `implement/{story-id}` and pushes there.

If the first argument is missing, use `AskUserQuestion` to request the plan path.

Derive the **project root** as the directory containing the implementation plan (or its parent if the plan is inside a `specs/` subdirectory). All relative paths in the plan and specs are resolved from this root.

---

## Resumability Protocol

Before starting any phase, check if `implementation-progress.json` exists in the same directory as the implementation plan.

If the file exists, read it and determine the current state:

- **`phase: "identify"`** — Phase 1 completed. The story has been selected. Skip to Phase 2.
- **`phase: "implement"`** — Phase 2 was in progress. Run `git diff --stat` to see what was already written. Resume Phase 2 using the spec and diff as context.
- **`phase: "verify"`** — Phase 3 was in progress. Skip to Phase 3 (re-run builds and tests).
- **`phase: "complete"`** — Previous story finished. Delete the progress file and start fresh from Phase 1 to pick the next story.

If the file does not exist, start from Phase 1.

**Print a status line when resuming:** `Resuming story: {storyId} — phase: {phase}`

---

## Execution Phases

Run these four phases sequentially. Do not skip phases (unless resuming — see above).

---

### Phase 1 — Identify Next Task

**Goal:** Find the first actionable unchecked story and verify its dependencies are met.

#### Step 1: Read the plan

Read `IMPLEMENTATION-PLAN.md` in full. Parse the story list entries looking for checkbox patterns.

#### Step 2: Find the first unchecked item

Scan for the first line matching `- [ ] **` — this is the next story to implement.

If **no** unchecked items exist, print:

```
All stories complete. Implementation plan is fully checked off.
```

Exit without error.

#### Step 3: Parse story metadata

From the matched entry and its indented sub-lines, extract:

- **storyOrder** — the number after `**` (e.g., `1` from `**1. project-setup**`)
- **storyId** — the slug identifier (e.g., `project-setup`)
- **specLink** — the relative path in the markdown link (e.g., `specs/stories/project-setup.md`)
- **priority** — P0, P1, or P2
- **dependencies** — list of story IDs from the "Depends on:" line
- **phaseScope** — if the link contains a `#fragment` (e.g., `#p1-scope`), record it — this story has multiple phases and we only implement the scoped phase

#### Step 4: Verify dependencies

For each dependency, check that its corresponding entry in the plan is `- [x]` (checked). If any dependency is still unchecked:

```
Blocked: story "{storyId}" depends on unchecked stories: {list}
Cannot proceed until dependencies are complete.
```

Exit without error.

#### Step 5: Write progress file

Write `implementation-progress.json` in the same directory as the plan:

```json
{
  "phase": "identify",
  "storyId": "project-setup",
  "storyOrder": 1,
  "specLink": "specs/stories/project-setup.md",
  "phaseScope": null,
  "priority": "P0",
  "dependencies": [],
  "straightToMaster": false,
  "buildAttempts": 0,
  "testFailures": 0
}
```

#### Step 6: Create branch (if not `--straight-to-master`)

If `--straight-to-master` was **not** passed:

1. Ensure you are on the main branch and it is up to date: `git pull`
2. Create and switch to a feature branch: `git checkout -b implement/{storyId}`

If `--straight-to-master` **was** passed, stay on the current branch.

#### Step 7: Announce

Print:

```
Next story: #{storyOrder} {storyId} (Priority: {priority})
Spec: {specLink}
Dependencies: {deps or "None"}
Branch: implement/{storyId} (or main with --straight-to-master)
```

---

### Phase 2 — Implement

**Goal:** Read the spec and all necessary context, then implement the story.

#### Step 1: Read context files

Read these files in order:

1. **The spec file** — resolve `specLink` relative to the plan directory. If `phaseScope` is set, focus on the matching `## Phase Scope` subsection but still read the full spec for context.
2. **CLAUDE.md** — look for it in the project root. This contains repo conventions, file structure, tooling commands, and patterns that must be followed.
3. **Cross-Cutting Concerns** — re-read the "Cross-Cutting Concerns" section of the implementation plan. These are rules every story must follow.

If the spec references specific sections of a technical architecture document, read those sections too.

#### Step 2: Understand what to build

From the spec, identify:

- **File paths** — new files to create and existing files to modify (from the spec's "File Paths" section)
- **Data model** — entities, schemas, migrations
- **API design** — endpoints, request/response shapes
- **UI components** — components, their states, their props
- **Acceptance criteria** — the specific behaviors that must work when done
- **Test plan** — what tests to write or update

#### Step 3: Read existing code

Before writing any code, read the files that will be modified. Read sibling files and imports to understand the existing patterns. Follow the conventions already established in the codebase — do not introduce new patterns unless the spec requires it.

#### Step 4: Implement

Write the code. Follow these principles:

- **Match existing patterns** — look at how adjacent features are built and follow suit
- **Spec is the contract** — implement what the spec says, not more, not less
- **Acceptance criteria are mandatory** — every AC must be satisfied
- **File paths from spec are authoritative** — create files where the spec says
- **Write tests as you go** — unit tests, integration tests as specified in the test plan
- **Handle cross-cutting concerns** — auth, error handling, offline patterns per the implementation plan

#### Step 5: Update progress

Update `implementation-progress.json`: set `"phase": "implement"`.

---

### Phase 3 — Verify

**Goal:** Ensure all apps and libraries build, and all tests pass.

#### Step 1: Build verification

Run the project's build command. Detect the correct command by reading `CLAUDE.md`, `package.json`, or `project.json`:

- **NX monorepo:** `npx nx run-many --target=build --all` or `npx nx affected --target=build`
- **Standard npm:** `npm run build`
- **Other:** whatever `CLAUDE.md` specifies

If the build **fails**:

1. Read the error output carefully
2. Diagnose the root cause — import errors, type errors, missing dependencies
3. Fix the issue in the source code
4. Increment `buildAttempts` in the progress file
5. Re-run the build

**Bail-out:** If the build fails after **2 fix attempts** (3 total builds), stop and report:

```
Build failing after 2 fix attempts. Manual intervention needed.
Errors: {summary of remaining build errors}
```

Exit without continuing to tests.

#### Step 2: Run tests

Run the project's test command. Detect from `CLAUDE.md` or project config:

- **Playwright:** `npx playwright test` or the project-specific command
- **NX:** `npx nx run-many --target=test --all` or `npx nx affected --target=test`
- **Jest:** `npx jest` or `npm test`

If tests **fail**:

1. Count the number of failing tests
2. If **more than 5 tests fail**, stop and report — this likely indicates a deeper issue:

```
{N} tests failing — exceeds threshold (max 5). Manual intervention needed.
Failing tests:
  - {test name 1}
  - {test name 2}
  ...
```

3. If **5 or fewer tests fail**, analyze each failure:
   - Is it a regression caused by this story's changes? → Fix it
   - Is it a pre-existing failure unrelated to this story? → Note it and move on
   - Is it a test that needs updating because behavior intentionally changed? → Update the test
4. After fixes, re-run the full test suite
5. Increment `testFailures` in the progress file

**Bail-out:** If tests still fail after **2 fix-and-rerun cycles**, stop and report:

```
Tests still failing after 2 fix cycles. Manual intervention needed.
Remaining failures:
  - {test details}
```

#### Step 3: Update progress

Update `implementation-progress.json`: set `"phase": "verify"`.

---

### Phase 4 — Complete

**Goal:** Update the implementation plan, commit, and push.

#### Step 1: Update the implementation plan

Edit `IMPLEMENTATION-PLAN.md`: change the completed story's `- [ ]` to `- [x]`.

Match the **exact line** for this story. For multi-phase stories, only check off the specific phase entry (e.g., `offline-data-layer (P0)`), not other phases of the same story.

#### Step 2: Commit

Stage all changed files. **Exclude** the progress file (`implementation-progress.json`) from the commit.

Write a commit message following this format:

```
feat({storyId}): {one-line summary of what was implemented}

Implements story #{storyOrder} from the implementation plan.
- {key change 1}
- {key change 2}
- {key change 3}

Spec: {specLink}
```

If `CLAUDE.md` specifies a different commit convention, follow that instead.

#### Step 3: Push

**If `--straight-to-master` was passed:**

1. Push directly to the current branch: `git push`

**If `--straight-to-master` was NOT passed:**

1. You are already on `implement/{storyId}` (created in Phase 1, Step 6)
2. Push with upstream tracking: `git push -u origin implement/{storyId}`
3. Print: `Pushed to branch: implement/{storyId}`

#### Step 4: Clean up

Delete `implementation-progress.json` — the story is complete.

Print a completion summary:

```
Story Complete
════════════════════════════════════════
Story:    #{storyOrder} {storyId}
Priority: {priority}
Spec:     {specLink}
Branch:   implement/{storyId} (or main)
Commit:   {short hash}
════════════════════════════════════════
```

---

## Error Handling & Bail-Outs

This skill has deliberate stopping points to avoid runaway fix cycles:

| Situation | Threshold | Action |
|---|---|---|
| Build fails repeatedly | 2 fix attempts (3 total builds) | Stop, report errors |
| Many tests fail | >5 test failures | Stop, report — likely deeper issue |
| Test fixes not working | 2 fix-and-rerun cycles | Stop, report remaining failures |
| Dependencies unmet | Any unchecked dependency | Stop, report which deps are missing |
| No unchecked stories | All items `[x]` | Print completion message, exit |

When the skill stops due to a bail-out, the progress file is preserved so the user can:
1. Investigate and fix manually
2. Re-run `/implementation` to resume from the current phase

---

## Context Window Strategy

This skill processes one story at a time, keeping context manageable.

### Token Budget

| Phase | Operations | Estimated Tokens |
|---|---|---|
| Phase 1 (identify) | Read plan, parse entries | ~8,000 |
| Phase 2 (implement) | Read spec + CLAUDE.md + source files, write code | ~60,000 |
| Phase 3 (verify) | Run builds/tests, read errors, fix code | ~40,000 |
| Phase 4 (complete) | Edit plan, commit, push | ~5,000 |
| **Total** | | **~113,000** |

### Protective Rules

1. **Read only the target spec** — Do not read other story specs. The current spec contains all requirements for this story.

2. **Read only necessary source files** — Before modifying a file, read it. Do not pre-read the entire codebase.

3. **Do not read test output in full** — When tests fail, read only the failure summary, not the entire test log. Use `--reporter=list` or equivalent for concise output.

4. **Do not re-read the implementation plan after Phase 1** — Story metadata is captured in the progress file.

5. **Limit build error analysis** — Read the first 100 lines of build errors. Build failures tend to cascade from a root cause at the top.

---

## Dependencies

This skill depends on:
- **refinement skill** — produces the implementation plan and story specs that this skill consumes
- **A project with build and test infrastructure** — NX, npm scripts, Playwright, or equivalent
