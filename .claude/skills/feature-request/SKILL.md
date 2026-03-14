---
name: feature-request
description: "Accept a user story as a feature request, validate it against the competitor analysis and technical architecture, generate a story spec in specs/stories/, and update IMPLEMENTATION-PLAN.md with the new feature. Ensures new features stay aligned with product strategy and architecture."
user_invocable: true
---

# Feature Request Skill

Accept a user story as a feature request, validate it against foundational project documents, produce an implementation-ready story spec, and insert the new feature into the existing implementation plan. Every feature request is checked against the competitor analysis report and technical architecture to prevent strategic or architectural drift.

## Argument Handling

```
/feature-request [--priority P0|P1|P2]
```

- **`--priority` flag** (optional): Override the auto-detected priority. Defaults to P1 if not specified and not determinable from context.

The skill will prompt the user for a user story using `AskUserQuestion`. This is intentional — feature requests should be articulated conversationally, not passed as file paths.

---

## Resumability Protocol

Before starting any phase, check if `feature-request-progress.json` exists in the `specs/` directory.

If the file exists, read it and determine the current state:

- **`phase: "intake"`** — Phase 1 completed. Skip to Phase 2.
- **`phase: "alignment"`** — Phase 2 completed. Skip to Phase 3.
- **`phase: "spec"`** — Phase 3 completed. Skip to Phase 4.
- **`phase: "plan"`** — Phase 4 completed. Skip to Phase 5.
- **`phase: "complete"`** — All phases done. Print the summary and exit.

If the file does not exist, start from Phase 1.

**Print a status line when resuming:** `Resuming from phase: {phase} — feature: {featureId}`

---

## Execution Phases

Run these five phases sequentially. Do not skip phases (unless resuming — see above).

---

### Phase 1 — Intake

**Goal:** Collect the feature request from the user and establish context.

#### Step 1: Prompt for user story

Use `AskUserQuestion` to ask the user for their feature request in user story format:

```
Please describe the feature you'd like to request.

Use the format: "As a [persona], I want to [action] so that [outcome]."

You can also include:
- Additional context or motivation
- Specific acceptance criteria
- Related features or areas of the product
```

#### Step 2: Parse the input

From the user's response, extract:

- **userStory** — the "As a... I want to... so that..." statement (compose one if the user gives a free-form description)
- **persona** — the user role from the story
- **action** — what the user wants to do
- **outcome** — the value they expect
- **additionalContext** — any extra detail the user provided
- **acceptanceCriteria** — any criteria the user specified (may be empty)

#### Step 3: Generate feature ID

Create a slug identifier from the action (e.g., `bulk-task-reassignment`, `real-time-alerts`, `offline-report-export`). Check if `specs/stories/{id}.md` already exists — if so, append a numeric suffix (e.g., `bulk-task-reassignment-2`).

#### Step 4: Write progress file

Write `specs/feature-request-progress.json`:

```json
{
  "phase": "intake",
  "featureId": "bulk-task-reassignment",
  "priority": "P1",
  "userStory": "As a shift manager, I want to bulk-reassign tasks so that I can respond to crew changes quickly.",
  "persona": "Shift Manager",
  "additionalContext": "...",
  "acceptanceCriteria": [],
  "timestamp": "2026-02-24T12:00:00Z"
}
```

---

### Phase 2 — Alignment Validation

**Goal:** Read the foundational documents and validate the feature request doesn't deviate from product strategy or architecture.

#### Step 1: Locate foundational documents

Scan `specs/` for:

1. **`competitor-analysis-report.md`** — Use `Glob` with pattern `specs/**/competitor-analysis-report.md`
2. **`technical-architecture.md`** — Use `Glob` with pattern `specs/**/technical-architecture.md`

If `competitor-analysis-report.md` is not found, also check the project root and common locations (`docs/`, `./`). If still not found, use `AskUserQuestion` to request its path. If the user confirms there is no competitor analysis, note this and proceed with architecture-only validation.

If `technical-architecture.md` is not found, also check the project root. If still not found, use `AskUserQuestion` to request its path. If the user confirms there is no tech arch, warn that alignment cannot be fully validated and proceed.

#### Step 2: Read and analyze competitor analysis

Read `competitor-analysis-report.md` in full. Extract:

- **Market gaps** — all identified gaps with severity
- **Differentiation pillars** — the strategic themes
- **Pain points** — top user pain points by frequency
- **Strategic insights** — recommended differentiators

Map the user's feature request to these elements:

- Does the feature address an identified market gap? Which one(s)?
- Does it align with a differentiation pillar?
- Does it address a known pain point?
- Does it introduce scope that contradicts the strategic direction?

#### Step 3: Read and analyze technical architecture

Read `technical-architecture.md` in full. Extract:

- **Architecture patterns** — hexagonal, layered, event-driven, etc.
- **Data model** — entities, relationships, tenant isolation
- **API conventions** — REST, auth, error handling patterns
- **NFRs** — non-functional requirements
- **Tech stack** — languages, frameworks, infrastructure

Map the user's feature request to these elements:

- Which architecture sections are relevant?
- Does the feature fit within existing patterns or require new ones?
- What data model changes are needed?
- What API endpoints would be required?
- Are there NFRs that constrain the implementation?

#### Step 4: Scan existing stories

Scan `specs/stories/` to understand what's already been planned:

1. Use `Glob` with pattern `specs/stories/*.md` to list all existing story specs
2. If an `IMPLEMENTATION-PLAN.md` exists, read it to understand the current story ordering, dependencies, and which stories are checked off

This establishes:
- What infrastructure/foundation stories exist that this feature can depend on
- Whether this feature overlaps with or extends an existing story
- Where in the dependency graph this feature should be inserted

#### Step 5: Alignment assessment

Produce an alignment assessment with three possible outcomes:

1. **Aligned** — Feature clearly maps to existing gaps, pillars, and architecture. Proceed.
2. **Aligned with Concerns** — Feature is broadly compatible but introduces minor novelty (new pattern, extends an existing gap in a new direction). Note concerns and proceed.
3. **Deviation Detected** — Feature conflicts with strategic direction or requires significant architectural changes not anticipated by the tech arch.

If **Deviation Detected**, present the concerns to the user via `AskUserQuestion`:

```
Alignment Check — Potential Deviation Detected
================================================
Feature: {featureId}

Concerns:
- {concern 1 — e.g., "No market gap supports this feature in the competitor analysis"}
- {concern 2 — e.g., "Requires a new data model pattern not covered by the tech arch"}

Options:
1. Proceed anyway — I'll document the deviation in the spec
2. Modify the feature — tell me what to adjust
3. Cancel — abandon this feature request

How would you like to proceed?
```

#### Step 6: Update progress

Update `feature-request-progress.json`:
- Set `"phase": "alignment"`
- Add `"alignmentStatus"`: "aligned" | "aligned-with-concerns" | "deviation-acknowledged"
- Add `"relatedGaps"`: list of gap titles from competitor analysis
- Add `"relatedArchSections"`: list of tech arch section numbers
- Add `"existingDependencies"`: list of story IDs this feature depends on
- Add `"competitorAnalysisPath"`: path to the competitor analysis file
- Add `"techArchPath"`: path to the technical architecture file

---

### Phase 3 — Generate Story Spec

**Goal:** Produce a complete implementation spec for the feature request.

#### Step 1: Load context

1. Read `feature-request-progress.json` for all collected data
2. Re-read the relevant sections of `technical-architecture.md` (only the sections identified in Phase 2)
3. If Storybook stories exist (check with `Glob` for `**/*.stories.tsx`), scan for components that relate to this feature

#### Step 2: Determine priority

Assign priority based on:
1. If `--priority` was passed, use that
2. If the feature addresses a "Critical" severity gap → P0
3. If the feature addresses a "Significant" severity gap → P1
4. If the feature addresses an "Emerging" gap or no gap → P2
5. Default to P1

#### Step 3: Generate acceptance criteria

If the user provided acceptance criteria in Phase 1, use them as a starting point. Expand or supplement with:
- Testable criteria derived from the user story
- Edge cases implied by the technical architecture
- Criteria that satisfy relevant NFRs

Aim for 3-6 acceptance criteria per requirement.

#### Step 4: Write the spec

Read the spec template from `references/spec-template.md` (relative to this skill).

Write the spec to `specs/stories/{featureId}.md` following the template exactly. Key requirements:

- **Alignment Check section is mandatory** — document how this feature maps to the competitor analysis and tech arch
- **User story must be preserved** — use the exact story from the user, then expand with acceptance criteria
- **File paths must be concrete** — reference the project's actual directory structure from the tech arch
- **Dependencies must be accurate** — reference existing story IDs from the scan in Phase 2
- **Technical approach must follow existing patterns** — cite tech arch sections, not invent new patterns

#### Step 5: Self-verify

After writing the spec:
1. Read back the file and confirm all template sections are present
2. Verify the alignment check section cites specific gaps and architecture sections
3. Verify acceptance criteria are testable
4. Verify file paths follow the project's conventions

#### Step 6: Update progress

Update `feature-request-progress.json`:
- Set `"phase": "spec"`
- Add `"specFile"`: `"specs/stories/{featureId}.md"`

---

### Phase 4 — Update Implementation Plan

**Goal:** Insert the new feature into the existing implementation plan, or create one if it doesn't exist.

#### Step 1: Locate the implementation plan

Look for `IMPLEMENTATION-PLAN.md` in:
1. The `specs/` directory
2. The project root
3. Common locations (`docs/`, `./`)

#### Step 2a: If IMPLEMENTATION-PLAN.md exists — Update it

Read the existing plan in full. Determine:

1. **Current story count** — how many stories are in the plan
2. **Next order number** — the highest existing order number + 1
3. **Dependency insertion point** — where in the plan this feature should appear based on its dependencies
4. **Checked-off stories** — which stories are already complete (`- [x]`)

**Insertion rules:**
- Place the new story **after** all of its dependencies in the list
- Place it **before** any existing stories that might depend on the same infrastructure but have higher order numbers
- If the feature has no dependencies on existing stories, place it after the last foundation/infrastructure story
- Never reorder existing stories — only insert the new one at the right position
- If the feature spans multiple priorities, create separate entries per phase (P0, P1, etc.)

Edit the plan to add the new story entry:

```markdown
- [ ] **{order}. {featureId}** — [{title}](specs/stories/{featureId}.md)
  - **Priority:** {priority}
  - **Persona:** {persona}
  - **Origin:** Feature Request
  - **Depends on:** {dependency IDs or "None"}
  - **Value delivered:** {one sentence — what works after this story ships}
  - **Key files:** {2-3 most important file paths from the spec}
```

Also update the **Dependency Graph** Mermaid diagram if one exists — add the new node and its dependency edges.

If a **Cross-Cutting Concerns** section exists, do NOT modify it unless the new feature introduces a genuinely new cross-cutting pattern (which should be rare for a single feature request).

#### Step 2b: If IMPLEMENTATION-PLAN.md does not exist — Create it

Write a new `IMPLEMENTATION-PLAN.md` in the `specs/` directory (or project root, following the project's convention). Include:

1. **Agent Workflow** section (same as the refinement skill's Phase 4 protocol)
2. The single story entry for this feature
3. A **Cross-Cutting Concerns** section extracted from the tech arch (if available)
4. A **Dependency Graph** Mermaid diagram showing the new story and its dependencies

```markdown
# Implementation Plan

## Agent Workflow

### How to Pick a Task

1. Read this plan and find the first unchecked item (`- [ ]`).
2. Verify all dependencies (listed after "Depends on:") are checked (`- [x]`).
3. If multiple items are available, work them in listed order — they are sorted by
   dependency and value.

### How to Execute a Task

1. Open the linked spec file. If it has a `## Phase Scope` section, read only the
   subsection for the current phase.
2. Read the project's CLAUDE.md for repo conventions.
3. Implement the requirements. Run tests. Ensure acceptance criteria pass.

### How to Mark Completion

1. Commit and push following repo conventions.
2. Edit this file: change `- [ ]` to `- [x]` for the completed item.
3. If only one phase of a multi-phase story is done, mark only that entry.

---

## Stories

- [ ] **1. {featureId}** — [{title}](specs/stories/{featureId}.md)
  - **Priority:** {priority}
  - **Persona:** {persona}
  - **Origin:** Feature Request
  - **Depends on:** {dependency IDs or "None"}
  - **Value delivered:** {one sentence}
  - **Key files:** {2-3 most important file paths from the spec}

---

## Cross-Cutting Concerns

{Extract from technical-architecture.md if available, otherwise note "See technical-architecture.md for project-wide patterns."}

---

## Dependency Graph

```mermaid
graph TD
    {featureId}["{title}"]
```
```

#### Step 3: Update SPEC-INDEX.md (if it exists)

If `SPEC-INDEX.md` exists in the `specs/` directory or project root, add an entry for the new story:

```markdown
| {order} | [{featureId}](specs/stories/{featureId}.md) | {title} | {priority} | {dependencies} | Pending |
```

#### Step 4: Update progress

Update `feature-request-progress.json`:
- Set `"phase": "plan"`
- Add `"planUpdated"`: true
- Add `"storyOrder"`: {order number in the plan}

---

### Phase 5 — Finalize

**Goal:** Summarize the feature request and clean up.

#### Step 1: Present summary

Print a completion summary:

```
Feature Request Complete
========================================
Feature:     {featureId}
Title:       {title}
Priority:    {priority}
Persona:     {persona}
Alignment:   {Aligned / Aligned with Concerns / Deviation Acknowledged}
Spec:        specs/stories/{featureId}.md
Plan:        IMPLEMENTATION-PLAN.md (story #{order})
========================================

Alignment Details:
- Market Gaps:  {gap titles or "N/A — no competitor analysis"}
- Architecture: Sections {section numbers or "N/A — no tech arch"}
- Dependencies: {dependency IDs or "None"}

Key Files (from spec):
- {file path 1}
- {file path 2}
- {file path 3}

Next: Run /implementation <path/to/IMPLEMENTATION-PLAN.md> to begin implementing.
```

#### Step 2: Clean up

Delete `feature-request-progress.json` — the feature request is complete. The spec and plan update are the durable artifacts.

#### Step 3: Update progress (final)

The progress file is already deleted. The phase is complete.

---

## Edge Cases

### No Competitor Analysis Report

If no `competitor-analysis-report.md` exists anywhere in the project:
- Skip competitor alignment validation
- Note in the spec's Alignment Check section: "N/A — no competitor analysis report found"
- Warn the user: "No competitor analysis report found. Feature alignment is based on technical architecture only. Consider running `/competitor-analysis` first for strategic validation."
- Proceed with architecture-only validation

### No Technical Architecture

If no `technical-architecture.md` exists:
- Warn the user that alignment cannot be validated
- Ask if they want to proceed without architecture validation
- If proceeding, the spec will have minimal technical approach details
- Recommend running `/technical-architecture` first

### Feature Overlaps with Existing Story

If the feature request closely matches an existing story in `specs/stories/`:
- Present the overlap to the user via `AskUserQuestion`
- Options: (1) Extend the existing spec, (2) Create a separate spec, (3) Cancel
- If extending, edit the existing spec to add the new requirements rather than creating a new file
- If extending, do NOT change the existing story's position in the implementation plan — just update the spec content

### No Implementation Plan Exists

If no `IMPLEMENTATION-PLAN.md` exists:
- Create one with the Agent Workflow protocol and the single new story
- This bootstraps the plan — subsequent `/feature-request` or `/refinement` runs will find and update it

### Feature Has No Clear Dependencies

If the feature doesn't depend on any existing stories:
- Set dependencies to "None"
- Place it after the last infrastructure/foundation story in the plan (or at position 1 if no plan exists)

### Feature Requires New Infrastructure

If the feature needs infrastructure not covered by existing stories (e.g., a new service, a new database):
- Split into two stories: (1) infrastructure story, (2) feature story that depends on it
- Generate specs for both
- Add both to the implementation plan in the correct order

### User Provides Multiple Features

If the user describes multiple features in one request:
- Use `AskUserQuestion` to clarify: "I see multiple features in your request. Should I create separate specs for each, or combine them into one story?"
- If separate, process them sequentially (one full pass through all phases per feature)
- If combined, merge into a single story with multiple acceptance criteria sections

---

## Context Window Strategy

This skill is lightweight by design — it processes a single feature at a time.

### Token Budget

| Phase | Operations | Estimated Tokens |
|---|---|---|
| Phase 1 (intake) | User interaction, parse input | ~3,000 |
| Phase 2 (alignment) | Read competitor analysis + tech arch + scan stories | ~25,000 |
| Phase 3 (spec generation) | Read template, write spec | ~15,000 |
| Phase 4 (plan update) | Read plan, edit plan | ~10,000 |
| Phase 5 (finalize) | Print summary, clean up | ~2,000 |
| **Total** | | **~55,000** |

### Protective Rules

1. **Read foundational documents once** — In Phase 2, read the competitor analysis and tech arch. Do not re-read them in later phases. Carry forward only the extracted mappings (gap IDs, section numbers).

2. **Do not read all existing specs** — In Phase 2 Step 4, only list the file names in `specs/stories/`. Read the implementation plan for ordering context, but do not read individual spec files unless checking for overlap.

3. **Single spec output** — This skill produces exactly one spec file (or extends one existing file). Unlike the refinement skill which batches many specs, this is a single-story operation.

4. **Minimal plan editing** — When updating the implementation plan, insert the new entry and update the Mermaid diagram. Do not rewrite or reformat existing entries.

---

## Dependencies

This skill works best when these documents exist (but gracefully handles their absence):
- **competitor-analysis skill** — produces `specs/competitor-analysis-report.md`
- **technical-architecture skill** — produces `technical-architecture.md`
- **refinement skill** (optional) — may have already produced `IMPLEMENTATION-PLAN.md` and `specs/stories/`
- **implementation skill** — consumes the updated `IMPLEMENTATION-PLAN.md` and story specs

## Reference Files

- `references/spec-template.md` — Template for feature story specs, includes the mandatory Alignment Check section
