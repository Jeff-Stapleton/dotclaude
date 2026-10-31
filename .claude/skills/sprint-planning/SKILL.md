---
name: sprint-planning
description: Plan a new sprint — roll over incomplete work, configure the view, set custom fields, and fill capacity from Epics. Use when the user asks to "plan a sprint", "sprint planning", "sprint-planning", "roll over sprint", or "set up next sprint".
version: 2.0.0
---

# Sprint Planning

## Overview

Plan a sprint in the Breeze Airways ClickUp workspace. This skill rolls over incomplete work from the previous sprint into the target sprint, configures the sprint view, sets custom fields, and optionally fills remaining capacity from the prioritized Epics backlog.

**Sprints cannot be created via the ClickUp API.** They are a special UI entity created either manually or via Sprint Automations. This skill assumes the target sprint already exists.

## Workspace Context

The Breeze Airways ClickUp workspace (Team ID: `2277049`) contains multiple product teams. Refer to **`references/workspace-structure.md`** for space IDs, sprint folder IDs, epics list IDs, custom field IDs, and naming conventions.

**Key architectural note:** Tasks live primarily in Epics/Backlog lists and are associated with sprint lists via ClickUp's **secondary locations** feature. To add a task to a sprint, use the ClickUp REST API to add it as a secondary location — do NOT create duplicate tasks.

## Prerequisites

- The `CLICKUP_API_TOKEN` environment variable must be set (personal API token, format: `pk_...`).
- Two ClickUp MCP servers are available:
  - **`clickup`** (basic) — `get_lists`, `get_tasks`, `search_tasks`, `create_task`, etc.
  - **`claude_ai_ClickUp`** — `clickup_search`, `clickup_filter_tasks`, `clickup_get_task`, etc.
- Direct ClickUp REST API calls via `curl` are needed for operations not covered by MCP tools.

## Critical API Gotchas

These are hard-won lessons. Do NOT skip this section.

1. **Finding tasks in sprints:** The basic MCP tools (`get_tasks`, `search_tasks`) return EMPTY for sprint lists because tasks are added via secondary locations. You MUST use `clickup_search` (from `claude_ai_ClickUp`) with `location.subcategories` filter to find sprint tasks.

2. **Status filtering is unreliable:** The `task_statuses` filter on `clickup_search` does NOT work correctly — it returns tasks of all statuses regardless of the filter. Always filter statuses **client-side** after fetching results.

3. **Sprint creation is impossible via API:** ClickUp Sprints are a special entity type with their own icon and behavior. The API only creates regular lists (`clickup_create_list_in_folder`), which have the wrong type. Sprints must be created manually in the UI or via Sprint Automations.

4. **Updating default views requires `name` and `type`:** When using `PUT /api/v2/view/{view_id}` on a required/default view, you MUST include `"name": "List"` and `"type": "list"` in the payload. Without them, the API returns `VIEWS_055` or `VIEWS_015` errors.

5. **Default views are lazily initialized:** The default "List" view (ID: `6-{list_id}-1`) only exists after someone opens the sprint in the ClickUp UI. If the view doesn't exist yet, the GET/PUT will fail. Ask the user to open the sprint in the UI first, then retry.

6. **Don't create named views — update the default one:** Creating a new view via `POST /api/v2/list/{list_id}/view` adds a separate tab. Instead, update the existing default "List" view via `PUT /api/v2/view/6-{list_id}-1`.

7. **Bash for loops:** Always inline task IDs directly in the `for` statement. Do NOT assign them to a variable first — variable expansion is unreliable in the tool's shell context.
   ```bash
   # CORRECT:
   for task_id in abc123 def456 ghi789; do ...; done

   # WRONG (IDs won't expand):
   TASK_IDS="abc123 def456 ghi789"
   for task_id in $TASK_IDS; do ...; done
   ```

## Procedure

### Step 1: Identify Team and Target Sprint

Ask the user which team to plan for using `AskUserQuestion`:
- **Operations**
- **SRE**
- **Operations Systems**
- **Trip Services**

Then identify the target sprint. The user may provide a direct URL, or you can find the latest sprint by listing the team's sprint folder:

```bash
# Use the basic MCP tool:
clickup.get_lists(folder_id: "<team_sprint_folder_id>")
```

The target sprint is the latest list in the folder (highest orderindex). Confirm with the user which sprint to plan.

Also identify the **previous sprint** (the one before the target) — this is the source for rollover tasks.

### Step 2: Configure the Sprint View

Update the target sprint's default "List" view to match the standard configuration.

**Step 2a:** Check if the view is initialized:
```bash
curl -s "https://api.clickup.com/api/v2/list/{sprint_list_id}/view" \
  -H "Authorization: ${CLICKUP_API_TOKEN}"
```
If `required_views.list` is `null`, ask the user to open the sprint in the ClickUp UI, then retry.

**Step 2b:** Once the view exists, update it. The view ID follows the pattern `6-{list_id}-1`:
```bash
curl -s -X PUT "https://api.clickup.com/api/v2/view/6-{sprint_list_id}-1" \
  -H "Authorization: ${CLICKUP_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "List",
    "type": "list",
    "grouping": {
      "field": "cf_ebbcffe8-2615-42b9-802f-885d47206a07",
      "dir": 1,
      "collapsed": [],
      "ignore": false,
      "single": false
    },
    "sorting": { "fields": [] },
    "filters": {
      "op": "AND",
      "fields": [],
      "search": "",
      "search_custom_fields": true,
      "search_description": true,
      "search_name": true,
      "show_closed": false
    },
    "columns": {
      "fields": [
        {"field": "assignee", "idx": 0, "width": 118, "hidden": false},
        {"field": "dueDate", "idx": 1, "width": 122, "hidden": false},
        {"field": "priority", "idx": 2, "width": 108, "hidden": true},
        {"field": "pointsEstimate", "idx": 3, "width": 124, "hidden": false, "calculation": {"func": "sum", "unit": "", "groups": []}},
        {"field": "name", "idx": 4, "width": 486, "hidden": true},
        {"field": "status", "idx": 5, "width": 133, "hidden": false},
        {"field": "id", "idx": 6, "width": 160, "hidden": true},
        {"field": "customId", "idx": 7, "width": 160, "hidden": true},
        {"field": "dateCreated", "idx": 8, "width": 160, "hidden": true},
        {"field": "dateDone", "idx": 9, "width": 160, "hidden": true},
        {"field": "dateUpdated", "idx": 10, "width": 160, "hidden": true},
        {"field": "startDate", "idx": 11, "width": 160, "hidden": true},
        {"field": "duration", "idx": 12, "width": 160, "hidden": true},
        {"field": "timeLogged", "idx": 13, "width": 160, "hidden": true},
        {"field": "timeEstimate", "idx": 14, "width": 160, "hidden": true},
        {"field": "sprints", "idx": 15, "width": 185, "hidden": true},
        {"field": "dateClosed", "idx": 16, "width": 160, "hidden": true},
        {"field": "createdBy", "idx": 17, "width": 160, "hidden": true},
        {"field": "latestComment", "idx": 18, "width": 160, "hidden": true},
        {"field": "commentCount", "idx": 19, "width": 160, "hidden": true},
        {"field": "lists", "idx": 20, "width": 185, "hidden": true},
        {"field": "pullRequests", "idx": 21, "width": 160, "hidden": true},
        {"field": "incompleteCommentCount", "idx": 22, "width": 160, "hidden": true},
        {"field": "customItems", "idx": 23, "width": 160, "hidden": true},
        {"field": "timeInStatus", "idx": 24, "width": 160, "hidden": true},
        {"field": "linked", "idx": 25, "width": 160, "hidden": true},
        {"field": "dependencies", "idx": 26, "width": 160, "hidden": true},
        {"field": "pages", "idx": 27, "width": 160, "hidden": true},
        {"field": "cf_2ec88f58-3567-4999-8d56-5ae5974cdc1f", "idx": 28, "width": 160, "hidden": true},
        {"field": "cf_721ae2d2-9979-4956-9cfa-d92f2ac06238", "idx": 29, "width": 160, "hidden": false},
        {"field": "cf_41395f7f-62fd-4683-a396-757f91653239", "idx": 30, "width": 160, "hidden": false},
        {"field": "cf_ebbcffe8-2615-42b9-802f-885d47206a07", "idx": 31, "width": 160, "hidden": true},
        {"field": "cf_d0ed3e14-5577-400d-9297-05ef44228cff", "idx": 32, "width": 160, "hidden": true},
        {"field": "tag", "idx": 33, "width": 160, "hidden": true}
      ]
    },
    "settings": {
      "show_task_locations": false,
      "show_subtasks": 1,
      "show_subtask_parent_names": false,
      "show_closed_subtasks": false,
      "show_assignees": false,
      "show_images": false,
      "show_timer": false,
      "collapse_empty_columns": false,
      "me_comments": true,
      "me_subtasks": true,
      "me_checklists": true,
      "show_empty_statuses": false,
      "auto_wrap": false,
      "time_in_status_view": 1,
      "is_description_pinned": false,
      "show_task_properties": true,
      "show_sprint_cards": {
        "show_add_tasks": true,
        "show_add_assignees": true,
        "show_add_estimates": true
      }
    }
  }'
```

**CRITICAL:** The `"name": "List"` and `"type": "list"` fields are REQUIRED for updating default views. Without them the API returns errors.

### Step 3: Roll Over Incomplete Tasks

Find all tasks in the **previous sprint** that are NOT "done (prod)" or "Closed", and add them to the target sprint.

**Step 3a:** Fetch all tasks from the previous sprint:
```
clickup_search(
  filters: {
    asset_types: ["task"],
    location: { subcategories: ["<previous_sprint_list_id>"] }
  },
  count: 100
)
```

**Important:** Do NOT use the `task_statuses` filter — it doesn't work. Fetch all tasks and filter client-side.

**Step 3b:** Filter results client-side. Keep every task where status is NOT:
- `done (prod)`
- `Closed`

All other statuses roll over: `todo`, `in progress`, `code review`, `product review`, `specing`, `unrefined`, `awaiting release`.

**Step 3c:** Present a summary table of tasks to roll over:

| # | Custom ID | Name | Status | Assignee |
|---|-----------|------|--------|----------|

**Step 3d:** Add each task to the target sprint as a secondary location:
```bash
# Inline all task IDs directly — do NOT use a variable
for task_id in <id1> <id2> <id3> ...; do
  result=$(curl -s -X POST "https://api.clickup.com/api/v2/list/<target_sprint_list_id>/task/${task_id}" \
    -H "Authorization: ${CLICKUP_API_TOKEN}" \
    -H "Content-Type: application/json")
  echo "${task_id}: ${result}"
done
```

A successful response returns `{}`.

### Step 4: Set Custom Fields on All Sprint Tasks

After rollover, set custom fields on ALL tasks in the target sprint (rolled-over + any that were already there).

**Step 4a:** Set "Unplanned" to "Planned" on every task:
```bash
for task_id in <all_sprint_task_ids>; do
  result=$(curl -s -X POST "https://api.clickup.com/api/v2/task/${task_id}/field/41395f7f-62fd-4683-a396-757f91653239" \
    -H "Authorization: ${CLICKUP_API_TOKEN}" \
    -H "Content-Type: application/json" \
    -d '{"value": 0}')
  echo "${task_id}: ${result}"
done
```

**Step 4b:** Check "Team" field on each task, and set to "On Deck" where undefined:
```bash
# First, check which tasks have Team undefined
for task_id in <all_sprint_task_ids>; do
  result=$(curl -s "https://api.clickup.com/api/v2/task/${task_id}?custom_fields=true" \
    -H "Authorization: ${CLICKUP_API_TOKEN}")
  team=$(echo "$result" | python3 -c "
import json,sys
d=json.load(sys.stdin)
for cf in d.get('custom_fields',[]):
    if cf['id']=='ebbcffe8-2615-42b9-802f-885d47206a07':
        v=cf.get('value')
        print('SET' if v is not None else 'UNDEFINED')
        break
" 2>/dev/null)
  echo "${task_id}: Team=${team}"
done
```

Then set "Team" = "On Deck" (value `2`) on tasks where it was UNDEFINED:
```bash
for task_id in <undefined_team_task_ids>; do
  result=$(curl -s -X POST "https://api.clickup.com/api/v2/task/${task_id}/field/ebbcffe8-2615-42b9-802f-885d47206a07" \
    -H "Authorization: ${CLICKUP_API_TOKEN}" \
    -H "Content-Type: application/json" \
    -d '{"value": 2}')
  echo "${task_id}: ${result}"
done
```

### Step 5: Final Summary

Present a complete sprint summary:

**Sprint Overview:**
- Sprint name and link
- Total tasks rolled over
- Tasks already in sprint before rollover

**All Sprint Tasks:** (table with Custom ID, name, status, assignee, Team, Unplanned)

## Custom Field Reference

| Field | Field ID | Values |
|-------|----------|--------|
| Team | `ebbcffe8-2615-42b9-802f-885d47206a07` | 0=Product, 1=Platform, 2=On Deck |
| Task Type | `721ae2d2-9979-4956-9cfa-d92f2ac06238` | 0=New Feature, 1=Bug, 2=Tech Debt, 3=Enhancement, ... |
| Unplanned | `41395f7f-62fd-4683-a396-757f91653239` | 0=Planned, 1=Unplanned, 2=TODO is all blocked, 3=On-Call Backlog |

## API Endpoint Reference

| Operation | Method | Endpoint |
|-----------|--------|----------|
| Add task to sprint | POST | `/api/v2/list/{list_id}/task/{task_id}` |
| Set custom field | POST | `/api/v2/task/{task_id}/field/{field_id}` |
| Get list views | GET | `/api/v2/list/{list_id}/view` |
| Update default view | PUT | `/api/v2/view/6-{list_id}-1` |
| Get task with fields | GET | `/api/v2/task/{task_id}?custom_fields=true` |
| Get lists in folder | GET | `/api/v2/folder/{folder_id}/list` |

## Additional Resources

### Reference Files
- **`references/workspace-structure.md`** — Space IDs, folder IDs, epics list IDs, custom field IDs, sprint cadence, and task status definitions
