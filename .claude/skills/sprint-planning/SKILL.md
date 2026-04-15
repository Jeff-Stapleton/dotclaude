---
name: sprint-planning
description: Create a new sprint and plan its work. Use when the user asks to "plan a sprint", "create a new sprint", "sprint planning", "sprint-planning", "roll over sprint", or "set up next sprint".
version: 1.0.0
---

# Sprint Planning

## Overview

Create a new sprint list in the Breeze Airways ClickUp workspace, roll over incomplete work from the previous sprint, configure the sprint view, and fill remaining capacity from the prioritized Epics backlog to hit a target point range.

## Workspace Context

The Breeze Airways ClickUp workspace (Team ID: `2277049`) contains multiple product teams. Refer to **`references/workspace-structure.md`** for space IDs, sprint folder IDs, epics list IDs, custom field IDs, and naming conventions.

**Key architectural note:** Tasks live primarily in Epics/Backlog lists and are associated with sprint lists via ClickUp's **secondary locations** feature. To add a task to a sprint, use the ClickUp REST API to add it as a secondary location — do NOT create duplicate tasks.

## Prerequisites

- The `CLICKUP_API_TOKEN` environment variable must be set (personal API token, format: `pk_...`).
- The ClickUp MCP server tools are available for creating lists, searching, and reading tasks.
- Direct ClickUp API calls via `curl` are needed for:
  - Adding tasks to sprint lists as secondary locations (`POST /api/v2/list/{list_id}/task/{task_id}`)
  - Creating/configuring views (`POST /api/v2/list/{list_id}/view`)

## Procedure

### Step 1: Select Team

Prompt the user to select which team to plan the sprint for. Use the `AskUserQuestion` tool with these options:

- **Operations**
- **SRE**
- **Operations Systems**
- **Trip Services**

Only one team per sprint planning session. Wait for the user's selection before proceeding.

### Step 2: Determine Sprint Number and Dates

Calculate the next sprint based on today's date and the biweekly cadence starting January 1, 2026:

1. Determine today's date.
2. Calculate which sprint is currently active (or just ending).
3. The new sprint starts the day after the current sprint ends.
4. Sprint duration is always 14 days (start date to end date, inclusive of start, exclusive of end for naming).

Look at the team's existing sprint folder to find the latest sprint list and confirm the next sprint number and dates. Use `clickup_get_workspace_hierarchy` filtered to the team's space, or use `clickup_search` to find recent sprints.

**Sprint naming convention:** `Sprint N (M/D - M/D)` — for example, `Sprint 6 (3/12 - 3/25)`.

Present the calculated sprint name to the user for confirmation before creating it.

### Step 3: Create the Sprint List

Use `clickup_create_list_in_folder` to create the new sprint list:
- **folder_id:** The team's 2026 Sprint Folder ID (from references)
- **name:** The sprint name from Step 2

Record the new list ID for subsequent steps.

### Step 4: Roll Over Incomplete Tasks from Previous Sprint

Find all tasks in the previous sprint that are not done:

1. Use `clickup_search` with the **previous sprint list ID as a subcategory location filter** and filter by `task_statuses: ["unstarted", "active"]`. Set `count: 100` to get all results.

2. From the results, identify tasks with incomplete statuses (todo, in progress). Ask the user if they also want to roll over tasks in `code review`, `product review`, or `specing` status.

3. For each task to roll over, add it to the new sprint list as a secondary location using the ClickUp REST API via Bash:
   ```bash
   curl -s -X POST "https://api.clickup.com/api/v2/list/{new_list_id}/task/{task_id}" \
     -H "Authorization: ${CLICKUP_API_TOKEN}" \
     -H "Content-Type: application/json"
   ```
   A successful response returns `{}`.

4. Run all curl commands in parallel for efficiency.

5. Calculate the total rollover points by fetching point values for each task (use `get_task` on individual tasks or batch via the REST API).

**Present a summary table** of rolled-over tasks showing: ID, name, status, assignee, and points.

### Step 5: Configure the Sprint View

Create a named list view on the new sprint with the standard configuration:

```bash
curl -s -X POST "https://api.clickup.com/api/v2/list/{new_list_id}/view" \
  -H "Authorization: ${CLICKUP_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sprint N Board",
    "type": "list",
    "grouping": {
      "field": "cf_ebbcffe8-2615-42b9-802f-885d47206a07",
      "dir": 1,
      "collapsed": [],
      "ignore": false,
      "single": false
    },
    "columns": {
      "fields": [
        {"field": "assignee", "idx": 0, "width": 109, "hidden": false},
        {"field": "pointsEstimate", "idx": 1, "width": 115, "hidden": false, "calculation": {"func": "sum", "unit": "", "groups": []}},
        {"field": "status", "idx": 2, "width": 147, "hidden": false},
        {"field": "cf_721ae2d2-9979-4956-9cfa-d92f2ac06238", "idx": 3, "width": 160, "hidden": false},
        {"field": "cf_41395f7f-62fd-4683-a396-757f91653239", "idx": 4, "width": 160, "hidden": false},
        {"field": "cf_ebbcffe8-2615-42b9-802f-885d47206a07", "idx": 5, "width": 160, "hidden": true}
      ]
    }
  }'
```

Replace `Sprint N Board` with the actual sprint name (e.g., `Sprint 6 Board`).

### Step 6: Fill from Epics Backlog

This is the core capacity planning step. The goal is to add sprint-ready subtasks from the highest-priority Epics until the sprint reaches the target point range.

#### 6a: Determine Target Points

Ask the user for their target point range. Default is **65-70 points** for Operations. Calculate remaining capacity:

```
remaining_capacity = target_max - rollover_points
```

#### 6b: Get the Prioritized Epics

Fetch all open tasks from the team's Epics list using the ClickUp REST API with subtasks:

```bash
curl -s -X GET "https://api.clickup.com/api/v2/list/{epics_list_id}/task?subtasks=true&include_closed=false&page=0" \
  -H "Authorization: ${CLICKUP_API_TOKEN}" \
  -H "Content-Type: application/json"
```

Paginate if `last_page` is false (increment `page` parameter).

**Epics are stack-ranked by `orderindex`** — lower orderindex = higher priority. Sort parent tasks (where `parent === null`) by `orderindex` ascending.

#### 6c: Identify Sprint-Ready Subtasks

For each epic (in priority order), examine its subtasks. A subtask is **sprint-ready** if:
1. It has a status of `todo`, `in progress`, or `code review` (actively workable)
2. It has **points assigned** (not null, not 0)
3. It is **not already in the new sprint** (check against already-added task IDs)

Skip subtasks that are `specing`, `unrefined`, or have no points — these aren't ready for sprint commitment.

#### 6d: Build the Sprint Backlog

Walk through epics top-to-bottom. For each epic's sprint-ready subtasks:
1. Add the subtask's points to a running total
2. If the running total would exceed the target max, consider whether to include it (slightly over is OK)
3. Stop when the target range is reached

Present the proposed additions as a table showing: task ID, name, parent epic, points, and running total. Ask the user for confirmation before adding.

#### 6e: Add Tasks to Sprint

After user confirmation, add each task to the new sprint list using the same REST API call from Step 4:

```bash
curl -s -X POST "https://api.clickup.com/api/v2/list/{new_list_id}/task/{task_id}" \
  -H "Authorization: ${CLICKUP_API_TOKEN}" \
  -H "Content-Type: application/json"
```

Run all curl commands in parallel for efficiency.

### Step 7: Final Summary

Present a complete sprint summary:

**Sprint Overview:**
- Sprint name and link
- Total points (rollover + new)
- Point breakdown: rollover vs new work

**Rollover Tasks:** (table with ID, name, status, assignee, points)

**New Tasks from Epics:** (table with ID, name, epic, assignee, points)

**Point Distribution:**
- By team (Product / Platform / On Deck) if data available
- By assignee

## Execution Guidelines

- Always begin with the interactive team selection in Step 1. Do not skip this.
- Always confirm the sprint name/dates with the user before creating the list.
- Use parallel tool calls and parallel curl commands wherever possible.
- When adding tasks to a sprint, use the REST API `POST /api/v2/list/{list_id}/task/{task_id}` — this adds a secondary location. Do NOT create duplicate tasks with `clickup_create_task`.
- The `CLICKUP_API_TOKEN` env var may not be available directly via `echo` — use `printenv | grep CLICKUP` to retrieve it if needed.
- On Windows, use `$TEMP` (not `/tmp`) for temporary files, and note that Node.js needs `process.env.TEMP` for file paths.
- When using Node.js for JSON parsing on Windows, write scripts to temp files first (avoid inline `-e` with special characters that bash escapes).
- A successful task-to-list addition returns `{}` from the API.
- If the API returns `{"err":"Team(s) not authorized"}`, the task ID is likely wrong — verify IDs from the actual API response data.
- Subtasks may span multiple pages in the Epics list — always check `last_page` and paginate.
- Present clear summary tables at each step so the user can verify before proceeding.

## Additional Resources

### Reference Files
- **`references/workspace-structure.md`** — Space IDs, folder IDs, epics list IDs, custom field IDs, sprint cadence, view configuration, and task status definitions
