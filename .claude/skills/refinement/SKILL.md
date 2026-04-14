---
name: refinement
description: "Validate a ClickUp task's readiness and size it using fibonacci points. Checks for user story/description and acceptance criteria, then suggests sizing with improvement recommendations."
user_invocable: true
---

# Refinement Skill

Validate ClickUp task readiness and suggest fibonacci story point sizing. For each task, checks that required elements (description and acceptance criteria) are present, suggests a size, and recommends improvements. Read-only — reports findings but does not modify ClickUp.

## Argument Handling

```
/refinement <clickup-task-url>
```

- **First argument** (required): A ClickUp task URL
- Extract `task_id` from the URL using the path segment after `/t/` (e.g., `https://app.clickup.com/t/86b3yxxxx` or `https://flybreeze.clickup.com/t/2277049/OPS-7379`)
- If the URL contains a workspace ID before the custom ID (e.g., `/t/2277049/OPS-7379`), extract both the `team_id` (`2277049`) and `task_id` (`OPS-7379`)
- **Custom task IDs** (e.g., `OPS-7379`): When calling `mcp__clickup__get_task` or `mcp__clickup__get_task_comments`, pass `team_id: "2277049"` alongside the `task_id`. This is required for the ClickUp API to resolve custom IDs.
- If the URL is a list/view URL (contains `/v/l/`) rather than a task URL (contains `/t/`), ask the user for a specific task URL instead
- If no URL is provided, use `AskUserQuestion` to request it

---

## Procedure

### Step 1 — Fetch the Task

Call `mcp__clickup__get_task` with the extracted `task_id`. From the response, note:
- `name`, `custom_id`, `status`, `assignees`, `description` (markdown), `points`
- `subtasks` array (if any)
- `parent` field (if this is a subtask)
- `custom_fields` (especially Task Type)

### Step 2 — Determine Scope

- **Parent/epic task** (has subtasks): Fetch each subtask via `mcp__clickup__get_task` in parallel. Process each subtask individually through Steps 3-5. The parent itself is NOT validated or sized — epics don't carry points.
- **Leaf task** (no subtasks, no parent): Process this single task through Steps 3-5.
- **Subtask** (has a parent): Process just this task through Steps 3-5. Note the parent task name for context.

If the epic has many subtasks (10+), present the summary table first and ask the user if they want the full detailed breakdown for each.

### Step 3 — Validate Readiness

For each task being processed, check two elements in the task description AND comments (fetch comments via `mcp__clickup__get_task_comments`):

#### 1. User Story / Description

Accept EITHER format:
- **Formal**: "As a [role], I want [capability], so that [benefit]"
- **Informal**: A clear description that explains what needs to be done and why — someone reading it can understand the work without asking follow-up questions

Flag as **MISSING** only if the description is empty or too vague to act on (e.g., just a title with no elaboration).

#### 2. Acceptance Criteria

Look for:
- A section labeled "Acceptance Criteria" or "AC" (case-insensitive)
- A bulleted or numbered list of testable conditions
- Check comments if not found in description

Flag as **MISSING** if no acceptance criteria can be identified anywhere.

#### Verdict

- All required elements present → **READY for sizing**
- Any required element missing → **"This story isn't ready to be sized"** with a list of what's missing

### Step 4 — Suggest Size (Only if READY)

Suggest a fibonacci size: **1, 2, 3, 5, 8, 13**

Analyze these signals:

| Signal | Where to find it |
|--------|-----------------|
| Number of acceptance criteria | Description/comments |
| External system integrations | Mentions of: NOC, Navblue, Mint, Trax, Oracle, ACARS, Sabre, Amadeus, SITA, Workday, GE Fuel, Proverne, Airline Choice |
| Task Type | Custom field `721ae2d2-9979-4956-9cfa-d92f2ac06238` |
| Complexity keywords | "migration", "refactor", "new API", "schema change", "new endpoint" = larger |
| Simplicity keywords | "simple", "update", "tweak", "config change", "rename" = smaller |
| Description scope | Length and breadth as a rough proxy |

**Sizing guide:**

| Points | Profile |
|--------|---------|
| **1** | Config change, single-field fix. 1-2 AC, no integrations. |
| **2** | Small bug fix or minor enhancement. 2-3 AC, 0-1 integrations. |
| **3** | Standard feature, well-defined scope. 3-4 AC, 1 integration. Most common size historically. |
| **5** | Multi-component feature, API + data changes. 4-6 AC, 1-2 integrations. |
| **8** | Cross-system integration, schema migration. 6+ AC, 2+ integrations. Consider recommending a split. |
| **13** | Too large — recommend decomposition into smaller stories. |

Present the suggested size with a brief rationale citing the specific signals observed. Always note that sizing is a suggestion — the team makes the final call.

### Step 5 — Suggest Improvements

For EVERY task (ready or not), provide actionable suggestions:

- **No formal user story?** Draft one based on the description (As a [inferred role], I want [what], so that [why])
- **Vague or broad AC?** Suggest more specific, testable criteria
- **AC items that could be separate tasks?** Recommend splitting
- **Description lacks context/why?** Suggest adding background
- **13 points?** Suggest how to decompose into smaller stories
- **Missing edge cases?** Suggest error handling, empty states, or boundary conditions to consider

---

## Output Format

### Single Task

```
## Refinement: {task name}
**Task:** {custom_id} | **Status:** {status} | **Assignee:** {assignee name}
**Type:** {Task Type value} | **Parent:** {parent name or "None"}

### Readiness Check
| Element             | Status       | Details                              |
|---------------------|-------------|--------------------------------------|
| User Story          | OK/MISSING  | {extracted story or what's needed}    |
| Acceptance Criteria | OK/MISSING  | {count of criteria or what's needed}  |

**Verdict:** READY for sizing / This story isn't ready to be sized

### Suggested Size
**{N} points** — {rationale}

Signals:
- {signal 1}
- {signal 2}
- {signal 3}

### Suggestions
- {actionable improvement 1}
- {actionable improvement 2}
```

### Epic with Subtasks

```
## Refinement: {epic name} (Epic)
**Task:** {custom_id} | **Subtasks:** {count}

| # | Subtask | Ready? | Size | Missing |
|---|---------|--------|------|---------|
| 1 | {name}  | Yes    | 3    | —       |
| 2 | {name}  | No     | —    | AC      |

**Summary:**
- Ready: {n} of {total} subtasks
- Not ready: {n} subtasks
- Total suggested points: {sum of sized subtasks}

{Per-subtask detailed breakdown using the single task format}
```

---

## Team Context

- **Fibonacci scale**: 1, 2, 3, 5, 8, 13
- **Historic distribution**: 95% of story points cluster at 2, 3, and 5
- **Sizing rule**: Only leaf subtasks carry points — parent/epic tasks are never sized
- **Task Type field ID**: `721ae2d2-9979-4956-9cfa-d92f2ac06238`
- **External systems** (complexity indicators): NOC, Navblue, Mint, Trax, Oracle, ACARS, Sabre, Amadeus, SITA, Workday, GE Fuel, Proverne, Airline Choice
- **Workspace/Team ID**: `2277049`
