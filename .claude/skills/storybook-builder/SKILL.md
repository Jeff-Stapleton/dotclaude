---
name: storybook-builder
description: "Build comprehensive Storybook stories for all pages and states defined in a product requirement brief. Uses the Moxy Design System (breeze-design skill), scaffolds Storybook config, and delegates page builds to subagents to manage context. Use when generating full Storybook coverage from a PRB."
---

# Storybook Builder Skill

Build complete Storybook coverage for every page and state defined in a product requirement brief (PRB). This skill orchestrates a multi-phase build that keeps context lean by parsing requirements into a manifest, delegating each page build to a subagent, and using a progress file as persistent state so the parent never reads subagent output or generated files.

## Argument Handling

```
/storybook-builder path/to/specs/product-requirement-brief.md
```

If the argument is missing, use `AskUserQuestion` to request the PRB path. The PRB is required input.

---

## Resumability Protocol

Before starting any phase, check if `storybook-progress.json` exists in the target project root.

If the file exists, read it and determine the current state:
- **`phase: "manifest"`** — Phase 1 completed. Skip to Phase 2.
- **`phase: "scaffold"`** — Phase 2 completed. Skip to Phase 3.
- **`phase: "build"`** — Phase 3 was in progress. Read the `pages` object — any page with `"status": "done"` is already built. Resume Phase 3, skipping completed pages.
- **`phase: "integration"`** — Phase 4 completed. Skip to Phase 5.
- **`phase: "complete"`** — All phases done. Print the summary from the progress file and exit.

If the file does not exist, start from Phase 1.

**Print a status line when resuming:** `Resuming from phase: {phase} — {n} of {total} pages already built`

---

## Execution Phases

Run these five phases sequentially. **Do not skip phases** (unless resuming — see above).

---

### Phase 1 — Parse PRB into Manifest

**Goal:** Extract a compact, structured manifest from the PRB so the full document never needs to stay in context.

1. Read the PRB file with the `Read` tool
2. Identify every page, view, or screen described across all epics and user stories
3. For each page, extract:
   - **name** — PascalCase component name (e.g., `FlightBoard`, `DisruptionLog`)
   - **feature** — the ops-fe feature domain it belongs to (maps to `libs/{feature}/`)
   - **persona** — the primary user persona from the PRB
   - **description** — one-sentence purpose
   - **states** — list of UI states this page must render (always include: `default`, `loading`, `empty`, `error`, plus domain-specific states from the PRB)
   - **keyData** — the data entities displayed (flights, passengers, crew, etc.)
   - **prbSection** — section number in the PRB for traceability
   - **prbLines** — `{ start, end }` line range in the PRB for this page's requirements
4. **Pre-compute batch assignments:** Group pages into batches of 3 and add a `batch` field (1-indexed) to each page entry. Add a top-level `totalBatches` field to the manifest.
5. Write the manifest to `storybook-manifest.json` in the target project root
6. **Initialize the progress file** — write `storybook-progress.json`:

```json
{
  "phase": "manifest",
  "totalPages": 15,
  "totalBatches": 5,
  "pages": {
    "FlightBoard": { "status": "pending", "batch": 1 },
    "DisruptionLog": { "status": "pending", "batch": 1 },
    ...
  }
}
```

7. Print a summary table of pages, state counts, and batch assignments for the user to review

**Before proceeding to Phase 2**, present the manifest summary and ask the user to confirm or adjust. Use `AskUserQuestion` if the PRB is ambiguous about page boundaries.

---

### Phase 2 — Scaffold Storybook Configuration

**Goal:** Set up Storybook infrastructure with Moxy Design System theming.

1. Read the config templates from `references/storybook-config-template.md`
2. Check if `.storybook/` already exists in the target project
   - If yes: merge Moxy decorators into existing `preview.ts`, do not overwrite
   - If no: scaffold the full `.storybook/` directory
3. Create these files (or verify they exist):
   - `.storybook/main.ts` — Vite builder, story globs, addons
   - `.storybook/preview.ts` — Moxy theme decorator, global CSS imports, viewport presets
   - `.storybook/manager.ts` — Breeze-branded Storybook UI theme
   - `.storybook/moxy-decorator.tsx` — shared wrapper providing Moxy CSS variables and fonts
4. Add Storybook scripts to `package.json` if missing:
   - `"storybook": "storybook dev -p 6006"`
   - `"build-storybook": "storybook build"`
5. **Update progress file** — set `"phase": "build"`

---

### Phase 3 — Build Pages and Stories (Subagent Delegation)

**Goal:** Build each page component and its Storybook stories without exhausting context.

**This phase follows the ultra-lean parent protocol. Read these rules carefully.**

#### Step 1: Load state (once)

1. Read `storybook-manifest.json` — this is the **only** time you read the manifest in Phase 3
2. Read `storybook-progress.json` — identify which pages are already `"done"` (from a resumed session) and which are `"pending"`
3. Build the batch plan in memory: for each batch number, collect the pending pages and their full manifest data

#### Step 2: Execute batches

For each batch of up to 3 pages, launch subagents **in parallel** using `Task` with `run_in_background: true`. Each subagent receives its page data **embedded directly in the prompt** — subagents never read the manifest.

**Subagent prompt template:**

```
You are building a React/TypeScript page component and its Storybook stories for Breeze Airways.

READ THESE FILES FIRST:
1. {absolute path to breeze-design SKILL.md} — Moxy Design System tokens, colors, typography, patterns
2. {absolute path to story-patterns.md} — Story file conventions, CSF3 format, state patterns
3. {absolute path to PRB} lines {prbLines.start}-{prbLines.end} — Requirements for this specific page

BUILD these 3 files:

1. Page component: libs/{feature}/{feature}-components/src/lib/{PageName}/{PageName}.tsx
   - Use Moxy Design System tokens (CSS variables, Tailwind classes)
   - Follow ops-fe conventions: export via barrel, use @ops-fe/ imports
   - Include TypeScript props interface with all data the page needs
   - Implement responsive layout (desktop 1280px+, tablet 768px+)

2. Story file: libs/{feature}/{feature}-components/src/lib/{PageName}/{PageName}.stories.tsx
   - CSF3 format with satisfies Meta<typeof {PageName}>
   - One named export per state: {states list}
   - Each story provides mock data via args
   - Include a docs page with usage notes

3. Barrel export: update libs/{feature}/{feature}-components/src/index.ts
   - Add export for {PageName} — do NOT touch any other exports in this file

Page details:
- Name: {name}
- Feature: {feature}
- Persona: {persona}
- Description: {description}
- States: {states joined with ", "}
- Key data: {keyData joined with ", "}

AFTER BUILDING — Self-verify:
1. Read back each file you created and confirm it compiles (imports resolve, types are correct)
2. Verify the story file has exactly {number of states} named exports (one per state)
3. Verify the barrel export includes {PageName}

THEN update storybook-progress.json:
- Read the current file
- Set pages.{PageName}.status to "done"
- Set pages.{PageName}.files to ["{component path}", "{story path}"]
- Set pages.{PageName}.storyCount to {number of stories you created}
- Write the file back

Return a single line: "DONE {PageName} — {N} stories" or "FAIL {PageName} — {error description}"
```

#### Step 3: Between batches

After all subagents in a batch complete, the parent does **exactly this** and nothing more:

1. **Read `storybook-progress.json`** (~500 tokens) to confirm batch completion
2. **Print a status line:** `Batch {n}/{total}: {page1} OK, {page2} OK, {page3} FAIL`
3. **Launch the next batch** (go to Step 2)

**DO NOT** do any of the following between batches:
- Do NOT read TaskOutput from subagents — the progress file is the source of truth
- Do NOT read any generated `.tsx` files — subagents self-verified
- Do NOT re-read the manifest — batch assignments were pre-computed in Step 1
- Do NOT read or edit `routes.tsx` or any routing file — that happens in Phase 4

#### Handling failures

If a page has `"status": "pending"` after its batch completes (subagent failed to update progress), mark it as `"status": "failed"` in the progress file and move on. Do not retry. The user can re-run the skill and resumability will skip completed pages.

---

### Phase 4 — Integration

**Goal:** Wire all completed page components into the application routing in a single pass.

Launch **one** Task subagent (`subagent_type: "general-purpose"`) with this prompt:

```
You are wiring completed Storybook page components into the application routing for Breeze Airways ops-fe.

READ THESE FILES:
1. storybook-manifest.json — page names, features, and file paths
2. storybook-progress.json — which pages were successfully built (status: "done")
3. The current routes file (e.g., apps/{app}/src/app/routes.tsx or equivalent)

FOR EACH page with status "done":
1. Add a lazy import for the page component
2. Add a route entry pointing to the component
3. Follow existing routing patterns in the file

IMPORTANT:
- Only add routes for pages with status "done" in the progress file
- Do not modify or remove any existing routes
- Follow the existing code style and patterns in routes.tsx
- Use React.lazy() for code splitting

After wiring all routes, update storybook-progress.json:
- Set "phase" to "integration"

Return a single line: "DONE — wired {N} routes"
```

After the subagent completes, read the progress file to confirm integration is done. Print: `Integration complete — {N} routes wired`

---

### Phase 5 — Validate and Report

**Goal:** Verify the build and give the user a coverage report.

1. Read `storybook-progress.json` for coverage data (page statuses, story counts)
2. Run `npx storybook build --test` (or the NX equivalent: `npx nx run {project}:build-storybook`) to check for compilation errors
3. Print a coverage report using data from the progress file:

```
Storybook Build Report
══════════════════════════════════════════
Page                States    Stories    Status
──────────────────────────────────────────
FlightBoard         6         6          OK
DisruptionLog       5         5          OK
CrewNotifications   4         3          PARTIAL (missing: error)
──────────────────────────────────────────
Total: 15/15 pages | 42/45 stories | 93% coverage
```

4. If any pages failed, list them with their status and suggest the user re-run `/storybook-builder` (resumability will skip completed pages)
5. Update progress file — set `"phase": "complete"`
6. Inform the user they can run `npm run storybook` to view the result

---

## Context Window Strategy

This skill is engineered to stay within the ~137k usable context window even for large PRBs (15+ pages).

### Token Budget

| Phase | Operations | Estimated Tokens |
|---|---|---|
| Phase 1 (parse PRB + manifest) | Read PRB, write manifest + progress | ~18,500 |
| Phase 2 (scaffold) | Read templates, write config files | ~8,000 |
| Phase 3 (build pages) | Read manifest once, read progress between batches | ~36,000 |
| Phase 4 (integration) | Launch one subagent | ~2,200 |
| Phase 5 (validate) | Read progress, run build, print report | ~5,000 |
| **Total** | | **~69,700** |

### Five Protective Rules

1. **Never read TaskOutput** — Subagents return one-line status strings. The progress file is the source of truth, not subagent output.

2. **Never read generated files** — Subagents self-verify their work (read back files, check exports, confirm story counts) before marking themselves as done.

3. **Never re-read the manifest** — Read it once at the start of Phase 3. Batch assignments are pre-computed in Phase 1 and held in memory.

4. **Never edit routes between batches** — Route wiring is deferred entirely to Phase 4's dedicated integration subagent.

5. **Only read the progress file between batches** — This is the single checkpoint mechanism. At ~500 tokens per read, 5 batch-gap reads cost ~2,500 tokens total.

---

## Dependencies

This skill depends on:
- **breeze-design skill** — read at `{skills-dir}/breeze-design/SKILL.md` by each subagent
- **microfrontend-nx skill** — conventions for file placement, imports, library structure
- **A product requirement brief** — the input document defining pages and requirements

## Reference Files

- `references/story-patterns.md` — CSF3 story format, standard state patterns, mock data conventions
- `references/storybook-config-template.md` — `.storybook/` directory boilerplate with Moxy theming
