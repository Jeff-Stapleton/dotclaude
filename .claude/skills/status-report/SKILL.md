---
name: status-report
description: This skill should be used when the user asks to "generate a status report", "create a sprint summary", "what happened last sprint", "sprint status", "status report", "sprint report", or discusses summarizing recent sprint work across teams
version: 2.2.0
---

# Project Status Report Generator

## Overview

Generate a project-level status report synthesizing recent work from the Breeze Airways ClickUp workspace. The report has exactly two sections: **Summary** and **Cross-Team Highlights**. It frames everything in terms of the broader project state — not sprints, not individual tickets.

## Core Framing Rules

These rules override any instinct toward ticket-level detail:

- **No individual ClickUp tickets.** Do not list task names, task IDs, or link to tasks. Tickets are source material, not output.
- **No sprint references.** Do not mention "this sprint", "last sprint", sprint names, sprint numbers, or sprint date ranges. The audience does not track sprints.
- **Frame in project terms.** Roll ticket-level work up into project initiatives, workstreams, capabilities, or outcomes. The reader should understand *what the project is currently doing and where it stands*, not *what tasks were closed*.
- **Present tense, current state.** Describe where things are now, not a chronological recap of the period.

## Workspace Context

The Breeze Airways ClickUp workspace (Team ID: `2277049`) contains multiple product teams, each with their own space and sprint folders. Refer to **`references/workspace-structure.md`** for the complete mapping of space IDs, sprint folder IDs, and naming conventions.

## Procedure

### Step 1: Select Report Scope

Prompt the user with `AskUserQuestion` to select which team(s) to include:

- **SRE**
- **Field Ops**
- **Central Ops**
- **Operations Systems**
- **Trip Services**
- **Sell**
- **Testing / QA**
- **Loyalty Experience**
- **All Teams**

Wait for the selection before proceeding.

### Step 2: Gather Source Data

Sprints are biweekly starting January 1, 2026, but this report runs weekly — pull tasks from the **current sprint list only**. Do not include the prior sprint. **The sprint is a data-gathering window only; it must not appear in the output.**

**Team sprint folder reference (2026 folder IDs):**

| Team | Sprint Folder ID | Notes |
|------|-----------------|-------|
| SRE | `90147510422` | Standard sprint naming |
| Field Ops | `90147563534` | Standard sprint naming. **Use the Step 2a workaround below instead of the sprint list** — see caveat |
| Central Ops | `901411992361` | Standard sprint naming (folder named "2026 Sprints"). **Use the Step 2a workaround below instead of the sprint list** — see caveat |
| Operations Systems | `90144086797` | May have empty sprints; skip if 0 tasks |
| Trip Services | `90144315292` | Called "Draws"; lists named "Services N" |
| Sell | `90147465093` | Standard sprint naming |
| Testing / QA | `90140225326` | Cumulative numbering (e.g., Sprint 62) |
| Loyalty Experience | `90147456951` | Themed names (e.g., "Avada Kedavra 3") |

For all teams except Field Ops and Central Ops: use `get_lists` to find the current sprint list, then `get_tasks` on it with **both** `include_closed: true` **and** `subtasks: true`. Subtasks are required — a lot of real work lives under parent stories, and omitting them produces misleadingly empty sprint views. When "All Teams" is selected, fetch lists and tasks for all teams in parallel.

### Step 2a: Field Ops / Central Ops Workaround (Sprint List Is Unreliable)

**Known limitation:** in these two spaces, sprint lists are populated mostly via ClickUp's "task in multiple lists" feature — the actual work items are subtasks whose primary home is the Backlog or Epics list, added into the sprint list on top of that. The available ClickUp MCP tools (`get_tasks`, `search_tasks`, `get_task`) only return a task's *primary* list membership — the `locations` field that should expose secondary list membership comes back empty. In practice this means `get_tasks` on the sprint list returns almost nothing (e.g. Central Ops Sprint 18 shows `task_count: 12` in list metadata but `get_tasks` only returns 2 of them). There is currently no reliable tool call to enumerate a sprint's actual task list for these two teams — do not attempt to use the sprint list as a data source for them.

**Workaround — pull from Backlog/Epics instead, filtered to active work:**

1. Get the Backlog and Epics list IDs for the team (Field Ops: Backlog `80047745`, Epics `900601272813`; Central Ops: Backlog `901419180254`, Epics `901419180255`).
2. Call `get_tasks` on each with `include_closed: true` and `subtasks: true`.
3. Filter the results to statuses that indicate active-or-recently-completed work (e.g. in progress, in review, code review, blocked, done, closed). Discard not-started/unrefined statuses (open, to do, unrefined, specing) — those are backlog noise, not current work.
4. Treat this filtered set as the proxy for "what's currently happening" for that team. It will not exactly match the official sprint roster count, and that's expected — do not try to reconcile counts.
5. Skip Step 3 enrichment cross-checks against sprint membership for these two teams, since sprint membership itself isn't reliably knowable; enrich based on task content and status only.

### Step 3: Enrich Where Needed

For tasks whose names are cryptic or which look like they might carry cross-team impact, call `get_task` to read the description. Cross-team signals include:
- Mentions of other team names
- Shared infrastructure, APIs, databases, deployment pipelines
- Migrations, schema changes, breaking changes
- Third-party integrations or vendor changes
- Payment/booking flow, loyalty program, or trip management touchpoints

### Step 4: Roll Tickets Up Into Project State

This is the critical synthesis step. Do not carry ticket names into the output.

For each team's tasks:
1. **Group tickets by initiative or workstream.** Cluster related tickets into the larger project goal they serve (e.g., "AWS migration", "payment flow hardening", "loyalty partner onboarding"). A cluster of 5 tickets about the same migration becomes one workstream.
2. **Summarize each workstream as a project state.** Describe where the workstream stands overall: what capability is being built or changed, and its current state (underway, nearing completion, stalled, recently shipped). Avoid ticket-level granularity.
3. **Identify cross-team implications.** For each workstream, ask: does this affect other teams' systems, surfaces, or commitments? If yes, note what the impact is and who is affected.

If a workstream can't be identified (one-off task with no obvious initiative), roll it into a general "operational work" bucket or omit it — do not list it individually.

### Step 5: Generate the Report

Use exactly the two sections below. No additional headings, no tables of ticket counts, no sprint metadata.

---

## Report Template

```
# Project Status Report
**Report Date:** [today's date]
**Scope:** [Selected team name, or "All Teams"]

---

## Summary

[A tight executive-level paragraph — 4 to 7 sentences, ~100 words max — covering: the main investment areas and roughly where each stands (in flight, shipped, stalled), anything notable that just wrapped, and the top one or two project-level risks. No bullets. No sprint language. Dense prose — every sentence should earn its place. If you find yourself writing a second paragraph, cut instead.]

---

## Cross-Team Highlights

[One-line items that other teams should know about. Formatting rules:
- Do NOT prefix with the originating team name (e.g., "**Operations** —"). It's redundant against the Scope line and gets deleted. When "All Teams" is selected and origin is ambiguous, group items under a small team sub-heading instead of prefixing each bullet.
- Do NOT append an "*Affects: ...*" clause. It tends to be speculative and noisy.
- Each bullet is just the project-level change or outcome, in one sentence.
- If nothing meaningfully crosses team boundaries, say so in one line rather than padding.]

- [Project-level change or outcome, one sentence.]
- ...
```

## Execution Guidelines

- Always begin with the Step 1 team selection prompt.
- Always fetch with `subtasks: true` in addition to `include_closed: true`. Current-sprint views will look empty otherwise.
- Only the current sprint is in scope — never fetch or reference the prior sprint.
- For Field Ops and Central Ops, always use the Step 2a Backlog/Epics workaround instead of the sprint list — do not attempt `get_tasks` on their sprint lists.
- When "All Teams" is selected, parallelize: fetch sprint lists (or Backlog/Epics lists, for Field Ops/Central Ops) for all teams in one batch, then fetch tasks for all resulting lists in one batch.
- Skip teams with no relevant work rather than including empty sections.
- **Summary is short.** Target ~100 words, one paragraph. Executives read the first two sentences. If it feels long, cut — don't reorganize.
- **Cross-Team Highlights** are terse one-liners. No originating-team prefix (it's redundant with Scope). No "Affects: ..." trailing clause (speculative and noisy). If nothing crosses team boundaries, say so in one line.
- When in doubt between "mention this ticket" and "omit it", omit it. The default bias is toward project-level framing.
- Never include task IDs, task URLs, sprint names, sprint numbers, or sprint date ranges in the output.

## Additional Resources

### Reference Files
- **`references/workspace-structure.md`** - Complete workspace hierarchy with all space IDs, folder IDs, list IDs, and naming conventions for every product team
