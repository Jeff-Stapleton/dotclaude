---
name: sprint-report
description: Generate sprint metrics for the most recent completed sprint. Use when the user asks to "generate a sprint report", "sprint metrics", "sprint numbers", "sprint-report", or needs sprint data for Excel.
version: 1.0.0
---

# Sprint Report Generator

## Overview

Generate sprint metrics from the Breeze Airways ClickUp workspace for the most recently completed sprint. Outputs tab-separated values suitable for pasting into an Excel spreadsheet.

## Workspace Context

The Breeze Airways ClickUp workspace (Team ID: `2277049`) contains multiple product teams. Refer to **`references/workspace-structure.md`** for space IDs, sprint folder IDs, and naming conventions. Refer to **`references/team-gitlab-mapping.md`** for GitLab group mappings.

## Output Metrics

The report produces these columns (tab-separated):

| Column | Definition |
|--------|-----------|
| Sprint Name | Name of the sprint list from ClickUp |
| Forecast | Total sprint points of tasks in the sprint on or before the start date (approximated as total points minus unplanned points) |
| Completed | Sprint points of tasks with status: complete, closed, done, or merged |
| Forecast Accuracy | `Completed / Forecast * 100` (as percentage) |
| Maintenance | Sprint points of tasks with Task Type = "Tech Debt" or "Security" |
| Maintenance % | `Maintenance / Completed * 100` (as percentage) |
| Unplanned | Sprint points of tasks with Unplanned custom field set to "Unplanned" |
| Unplanned % | `Unplanned / Completed * 100` (as percentage) |
| Bugs | Sprint points of tasks with Task Type = "Bug" |
| Bugs % | `Bugs / Completed * 100` (as percentage) |
| Avg MRs/Day | Total merged MRs during sprint period / working days (from GitLab) |

## Procedure

### Step 1: Select Team

Prompt the user to select which team to generate the sprint report for. Use the `AskUserQuestion` tool with these options:

- **SRE**
- **Operations**
- **Operations Systems**
- **Trip Services**
- **Sell**
- **Testing / QA**
- **Loyalty Experience**

Only one team per report. Wait for the user's selection before proceeding.

### Step 2: Identify the Most Recent Completed Sprint

Determine today's date. Using the biweekly sprint cadence starting January 1, 2026, calculate which sprint is **currently active** and which sprint **most recently completed** (the one before the current sprint).

Use the team's sprint folder ID from the reference table below to call `get_lists` and find the sprint list matching the most recently completed sprint dates.

**2026 Sprint Folder IDs:**

| Team | Folder ID |
|------|-----------|
| SRE | `90147510422` |
| Operations | `90147563534` |
| Operations Systems | `90144086797` |
| Trip Services | `90144315292` |
| Sell | `90147465093` |
| Testing / QA | `90140225326` |
| Loyalty Experience | `90147456951` |

Parse the sprint list name to extract the sprint date range. The start date and end date are needed for the GitLab MR query.

### Step 3: Retrieve All Tasks (Including Subtasks)

Call `get_tasks` on the identified sprint list with `include_closed: true` and `subtasks: true` to get all tasks and subtasks regardless of status. If there are many tasks, paginate using the `page` parameter (100 tasks per page, starting at page 0).

After collecting all items from `get_tasks`, compare the count against the list's `task_count` from the Step 2 `get_lists` response. If the returned count is significantly lower than `task_count`, subtasks may not have been fully returned. In that case:

1. For each parent task returned, call `get_task` on it to retrieve its full details including its `subtasks` array.
2. For each subtask ID found that is **not** already in the collected set, call `get_task` on that subtask ID to fetch its full details.
3. Batch these `get_task` calls in parallel where possible to minimize latency.

**Both parent tasks and subtasks count toward all metrics.** Every item (task or subtask) is treated identically for points, status, Task Type, and Unplanned classification. There is no special handling or exclusion for subtasks vs parent tasks.

Collect ALL tasks and subtasks before proceeding to calculations.

### Step 4: Enrich Task Details

For each task/subtask collected, check if it has sufficient data (points, custom fields, tags). The `get_tasks` response includes:
- `points` - sprint point value (may be null; treat null as 0)
- `tags` - array of tag objects with `name` property
- `custom_fields` - array of custom field objects
- `status` - object with `status` property (lowercase string)
- `parent` - if present/non-null, this item is a subtask

If any task is missing custom field data needed for classification, use `get_task` on that individual task to get full details. Batch these calls in parallel where possible.

### Step 4b: Filter Out "On Deck" Tasks

Before calculating metrics, filter out any tasks/subtasks where the **Team** custom field is set to **"On Deck"**.

**Team custom field:**
- **Field ID**: `ebbcffe8-2615-42b9-802f-885d47206a07`
- **Type**: `drop_down`
- **Options**:
  - Index `0` = Product
  - Index `1` = Platform
  - Index `2` = On Deck

**Remove** any task/subtask where this field's value is `2` (On Deck). These tasks are excluded from **all** metrics and counts. In the Step 8 supporting details, note how many tasks were excluded as "On Deck".

Tasks where the Team field is not set, or set to Product (`0`) or Platform (`1`), are kept.

### Step 5: Calculate Metrics

For each task and subtask, extract:
1. **Points**: `task.points` (default to 0 if null)
2. **Status**: `task.status.status` - use prefix matching since teams append qualifiers (e.g., `done (prod)`)
3. **Task Type**: Find the custom field with `id == "721ae2d2-9979-4956-9cfa-d92f2ac06238"` (dropdown). The value is an index into the `type_config.options` array:
   - Index `0` = New Feature
   - Index `1` = Bug
   - Index `2` = Tech Debt
   - Index `3` = Enhancement
   - Index `4` = Automation
   - Index `5` = Security
   - Index `6` = DevOps
   - Index `7` = UI/UX
   - Index `8` = Epic
   - Index `9` = Docs / training
   - Index `10` = Suggestion
   - Index `11` = New Report
   - Index `12` = 20% Project
   - Index `13` = Easter Egg
   - Index `14` = Rebuild
   - Index `15` = Testing
   - Index `16` = Analytics
4. **Unplanned**: Find the custom field with `id == "41395f7f-62fd-4683-a396-757f91653239"` (dropdown). Options:
   - Index `0` = Planned
   - Index `1` = Unplanned
   - Index `2` = TODO is all blocked
   - Index `3` = On-Call Backlog
   A task is "unplanned" when the value equals `1`.

**Completion statuses** - match with **prefix/startsWith** (case-insensitive) since teams use variants like `done (prod)`, `complete`, etc.: `done`, `complete`, `closed`, `merged`

Calculate each metric:

```
total_points      = sum of points for ALL tasks
unplanned_points  = sum of points for tasks where Unplanned custom field value == 1 ("Unplanned")
completed_points  = sum of points for tasks with a completion status
maintenance_points = sum of points for tasks with Task Type "Tech Debt" OR "Security"
bug_points        = sum of points for tasks with Task Type "Bug"

forecast          = total_points - unplanned_points
forecast_accuracy = (completed_points / forecast) * 100    [if forecast > 0, else "N/A"]
maintenance_pct   = (maintenance_points / completed_points) * 100  [if completed > 0, else 0]
unplanned_pct     = (unplanned_points / completed_points) * 100   [if completed > 0, else 0]
bugs_pct          = (bug_points / completed_points) * 100         [if completed > 0, else 0]
```

### Step 6: Calculate Avg MRs/Day from GitLab

Check the **`references/team-gitlab-mapping.md`** file for the selected team's GitLab group(s).

If the team has `TODO` as their GitLab mapping, inform the user that the GitLab mapping hasn't been configured for this team and output "N/A" for Avg MRs/Day. Suggest they update the mapping file.

If the mapping exists, for each GitLab group/project:

1. Extract the sprint start and end dates from the sprint name (format: `MM/DD - MM/DD`).
2. Convert to full ISO dates (add the year based on the sprint folder year).
3. Run via Bash:
   ```bash
   glab mr list --group <group-path> --state merged --after <start-date> --before <end-date> --per-page 100 --output json 2>/dev/null | python -c "import sys,json; print(len(json.load(sys.stdin)))"
   ```
   If `glab` is not installed or fails, try the GitLab API directly:
   ```bash
   curl --header "PRIVATE-TOKEN: $GITLAB_TOKEN" "https://<gitlab-host>/api/v4/groups/<group-id>/merge_requests?state=merged&created_after=<start>&created_before=<end>&per_page=100" 2>/dev/null | python -c "import sys,json; print(len(json.load(sys.stdin)))"
   ```
4. Sum the MR count across all groups for the team.
5. Calculate working days in the sprint period (exclude weekends). A standard 2-week sprint has 10 working days.
6. `avg_mrs_day = total_mrs / working_days`

If GitLab is unavailable or returns an error, output "N/A" for Avg MRs/Day and note the issue.

### Step 7: Output Results

Output the data in **two formats**:

**Format 1: Tab-separated for Excel (wrapped in a code block for easy copying)**

```
Sprint Name	Forecast	Completed	Forecast Accuracy	Maintenance	Maintenance%	Unplanned	Unplanned %	Bugs	Bugs %	Avg MRs/Day
[sprint name]	[forecast]	[completed]	[accuracy%]	[maintenance]	[maint%]	[unplanned]	[unplanned%]	[bugs]	[bugs%]	[mrs/day]
```

Rules for the tab-separated output:
- Use TAB characters between columns (not spaces)
- Percentages should be formatted as numbers with one decimal (e.g., `84.4` not `84.4%`) so Excel treats them as numbers
- Points should be integers
- MRs/Day should have one decimal place
- Include the header row

**Format 2: Readable summary table (for quick visual reference)**

Display the same data as a markdown table for readability.

### Step 8: Show Supporting Details

After the main output, show a brief breakdown:
- Total items in sprint: N (N parent tasks + N subtasks)
- Excluded as "On Deck": N (list names if fewer than 10)
- Items included in metrics: N
- Items with points: N
- Items without points: N (list names if fewer than 10)
- Unplanned items: N (list names)
- Maintenance items: N (list names)
- Bug items: N (list names)

This helps the user verify the numbers and catch any misclassified tasks.

## Execution Guidelines

- Always begin with the interactive team selection in Step 1. Do not skip this.
- Use parallel tool calls wherever possible (e.g., fetching task details for multiple tasks).
- If a sprint list has 0 tasks, inform the user and ask if they want to try a different sprint.
- **Subtasks are included in all metrics.** Both parent tasks and subtasks contribute to points, completion, Task Type, and Unplanned counts. Always pass `subtasks: true` when calling `get_tasks`, and verify the returned count against the list's `task_count`. If there is a discrepancy, fetch subtasks individually via `get_task` on each parent task (see Step 3 for details).
- Tasks/subtasks with null/missing points should be counted as 0 points but flagged in the supporting details.
- The Task Type custom field may not be set on all tasks. Tasks without a Task Type set are excluded from Maintenance and Bug counts (but still included in Forecast and Completed).
- For the "Unplanned" check, use the custom dropdown field (id: `41395f7f-62fd-4683-a396-757f91653239`), value `1` = Unplanned.
- When calculating Forecast Accuracy, if Forecast is 0, output "N/A".
- When calculating percentages, if the denominator (Completed) is 0, output 0.
- Round percentages to one decimal place.
- Round MRs/Day to one decimal place.

## Additional Resources

### Reference Files
- **`references/workspace-structure.md`** - Space IDs, folder IDs, sprint cadence, task statuses, and custom field IDs
- **`references/team-gitlab-mapping.md`** - GitLab group/project mapping per team (must be configured by user)
