---
name: storybook-builder
description: "Build comprehensive Storybook stories for all pages and states defined in a product requirement brief. Uses the Moxy Design System (breeze-design skill), scaffolds Storybook config, and delegates page builds to subagents to manage context. Use when generating full Storybook coverage from a PRB."
---

# Storybook Builder Skill

Build complete Storybook coverage for every page and state defined in a product requirement brief (PRB). This skill orchestrates a multi-phase build that keeps context lean by parsing requirements into a manifest, then delegating each page build to a subagent.

## Argument Handling

```
/storybook-builder path/to/specs/product-requirement-brief.md
```

If the argument is missing, use `AskUserQuestion` to request the PRB path. The PRB is required input.

## Execution Phases

Run these four phases sequentially. **Do not skip phases.**

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
4. Write the manifest to `storybook-manifest.json` in the target project root
5. Print a summary table of pages and state counts for the user to review

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

---

### Phase 3 — Build Pages and Stories (Subagent Delegation)

**Goal:** Build each page component and its Storybook stories without exhausting context.

Read `storybook-manifest.json`. For each page entry, launch a **Task subagent** (`subagent_type: "general-purpose"`) with this prompt template:

```
You are building a React/TypeScript page component and its Storybook stories for Breeze Airways.

READ THESE FILES FIRST:
1. {path to breeze-design SKILL.md} — Moxy Design System tokens, colors, typography, patterns
2. {path to story-patterns.md} — Story file conventions, CSF3 format, state patterns
3. {path to PRB} lines {start}-{end} — Requirements for this specific page

BUILD:
1. Page component: libs/{feature}/{feature}-components/src/lib/{PageName}/{PageName}.tsx
   - Use Moxy Design System tokens (CSS variables, Tailwind classes)
   - Follow ops-fe conventions: export via barrel, use @ops-fe/ imports
   - Include TypeScript props interface with all data the page needs
   - Implement responsive layout (desktop 1280px+, tablet 768px+)

2. Story file: libs/{feature}/{feature}-components/src/lib/{PageName}/{PageName}.stories.tsx
   - CSF3 format with satisfies Meta<typeof {PageName}>
   - One named export per state: {states from manifest}
   - Each story provides mock data via args
   - Include a docs page with usage notes

3. Barrel export: update libs/{feature}/{feature}-components/src/index.ts

Page details:
- Name: {name}
- Feature: {feature}
- Persona: {persona}
- Description: {description}
- States: {states}
- Key data: {keyData}
```

**Parallelism rules:**
- Launch up to 3 subagents concurrently using `run_in_background: true`
- Wait for all background agents to complete before launching the next batch
- After each batch, read the output files to check for errors

**If a subagent fails:** Read its output, diagnose the issue, and retry once with a corrected prompt. If it fails again, log the page name and move on — report failures in Phase 4.

---

### Phase 4 — Validate and Report

**Goal:** Verify the build and give the user a coverage report.

1. Run `npx storybook build --test` (or the NX equivalent: `npx nx run {project}:build-storybook`) to check for compilation errors
2. Count stories per page and compare against the manifest
3. Print a coverage report:

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

4. If any pages failed, list them with the error and suggest fixes
5. Inform the user they can run `npm run storybook` to view the result

---

## Context Window Strategy

This skill is designed to protect the context window:

- **Phase 1** reads the PRB once, extracts a manifest, then the PRB leaves context
- **Phase 2** reads config templates, writes files, templates leave context
- **Phase 3** delegates each page to a subagent with its own fresh context — the main context only holds the manifest (small JSON) and tracks progress
- **Phase 4** runs validation commands and prints a summary

The main context never holds more than: the manifest + one batch of subagent results at a time.

---

## Dependencies

This skill depends on:
- **breeze-design skill** — read at `{skills-dir}/breeze-design/SKILL.md` by each subagent
- **microfrontend-nx skill** — conventions for file placement, imports, library structure
- **A product requirement brief** — the input document defining pages and requirements

## Reference Files

- `references/story-patterns.md` — CSF3 story format, standard state patterns, mock data conventions
- `references/storybook-config-template.md` — `.storybook/` directory boilerplate with Moxy theming
