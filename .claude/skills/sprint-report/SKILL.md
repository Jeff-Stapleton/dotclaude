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
| Unplanned | Sprint points of tasks with Unplanned custom field set to "Unplanned" |
| Bugs | Sprint points of tasks with Task Type = "Bug" |
| Avg MRs/Day | Total merged MRs during sprint period / working days (from GitLab) |

The Maintenance %, Unplanned %, and Bugs % columns are intentionally NOT in the output — the destination Excel report computes them from the raw point columns. Do not output redundant percentage columns.

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

### Step 3: Retrieve All Tasks in the Sprint

**CRITICAL:** Tasks live primarily in Epics/Backlog lists and are associated with sprint lists via ClickUp's **secondary locations** feature. The basic `mcp__clickup__get_tasks` tool returns ONLY tasks whose home/primary list is the sprint — it MISSES every task added via secondary location, which is the vast majority. Do NOT use `get_tasks` for sprint reporting.

Use `mcp__claude_ai_ClickUp__clickup_search` with the `location.subcategories` filter — this returns every task associated with the sprint list, including those added via secondary locations and including subtasks:

```
mcp__claude_ai_ClickUp__clickup_search({
  filters: {
    asset_types: ["task"],
    location: { subcategories: ["<sprint_list_id>"] }
  },
  count: 100
})
```

Notes:
- **Do NOT use `task_statuses`** — that filter is broken on `clickup_search`. Filter status client-side later.
- If `next_cursor` is non-null, paginate with `cursor`.
- Each result includes `id`, `custom_id`, `name`, `status`, `archived`, but NOT points or custom fields.

### Step 4: Fetch Full Task Details (Points and Custom Fields)

`clickup_search` does not include points or custom fields. For each task ID returned, fetch full details via the ClickUp REST API in parallel:

```bash
for id in <id1> <id2> ...; do
  curl -s "https://api.clickup.com/api/v2/task/${id}?custom_fields=true" \
    -H "Authorization: ${CLICKUP_API_TOKEN}" \
    -o "/tmp/sprint_tasks/${id}.json" &
done
wait
```

(Inline IDs in the `for` statement — variable expansion is unreliable in the shell context.)

For each loaded task, extract:
- `points` — sprint points (may be null; treat null as 0)
- `status.status` — string status (lowercase)
- `parent` — null for parent task, populated for subtask
- `archived` — boolean
- `custom_fields[]` — find Task Type, Unplanned, Team by ID (see Step 5)

**Both parent tasks and subtasks count toward all metrics.** Treat them identically.

### Step 4b: Do NOT Exclude "On Deck" Tasks

**All tasks in the sprint count toward metrics, regardless of the Team custom field value.** Tasks with Team = "On Deck" are still real work that landed in the sprint, and they count toward Forecast, Completed, Bugs, Maintenance, and Unplanned just like any other task.

For reference, the Team custom field options are:
- Field ID: `ebbcffe8-2615-42b9-802f-885d47206a07`
- Options: Claude (0), Product (1), Platform (2), On Deck (3)

You may surface the Team breakdown in the Step 8 supporting details (e.g., "On Deck: N tasks, X pts") for informational purposes, but do not exclude any from the calculations.

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
```

Do NOT compute Maintenance %, Unplanned %, or Bugs % — those are calculated downstream in the Excel report from the raw point columns.

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
Sprint Name	Forecast	Completed	Forecast Accuracy	Maintenance	Unplanned	Bugs	Avg MRs/Day
[sprint name]	[forecast]	[completed]	[accuracy]	[maintenance]	[unplanned]	[bugs]	[mrs/day]
```

Rules for the tab-separated output:
- Use TAB characters between columns (not spaces)
- Forecast Accuracy is formatted as a number with one decimal (e.g., `74.3` not `74.3%`) so Excel treats it as a number
- All other point columns are integers
- MRs/Day should have one decimal place
- Include the header row
- Do NOT include Maintenance %, Unplanned %, or Bugs % — those are computed in the Excel report

**Format 2: Readable summary table (for quick visual reference)**

Display the same data as a markdown table for readability.

### Step 8: Show Supporting Details

After the main output, show a brief breakdown:
- Total items in sprint: N (N parent tasks + N subtasks)
- Items with points: N
- Items without points: N (list names if fewer than 10)
- Team breakdown (informational, not used for exclusion): Claude/Product/Platform/On Deck/unset counts and points
- Unplanned items: N (list names)
- Maintenance items: N (list names)
- Bug items: N (list names)

This helps the user verify the numbers and catch any misclassified tasks.

## Execution Guidelines

- Always begin with the interactive team selection in Step 1. Do not skip this.
- Use parallel tool calls wherever possible (e.g., fetching task details for multiple tasks via parallel `curl &; wait`).
- If a sprint search returns 0 tasks, inform the user and ask if they want to try a different sprint.
- **Use `clickup_search` with `location.subcategories`, NOT `get_tasks`.** Tasks are added to sprints as secondary locations; `get_tasks` only returns home-list tasks and will miss most of the sprint.
- **Subtasks are included in all metrics.** `clickup_search` returns parent tasks and subtasks together; treat them identically for points, status, Task Type, and Unplanned classification.
- Tasks/subtasks with null/missing points should be counted as 0 points but flagged in the supporting details.
- The Task Type custom field may not be set on all tasks. Tasks without a Task Type set are excluded from Maintenance and Bug counts (but still included in Forecast and Completed).
- For the "Unplanned" check, use the custom dropdown field (id: `41395f7f-62fd-4683-a396-757f91653239`), value `1` = Unplanned.
- When calculating Forecast Accuracy, if Forecast is 0, output "N/A". Round to one decimal place.
- Round MRs/Day to one decimal place.
- Do NOT compute or output Maintenance %, Unplanned %, or Bugs % — those are auto-computed downstream in Excel.

## Additional Resources

### Reference Files
- **`references/workspace-structure.md`** - Space IDs, folder IDs, sprint cadence, task statuses, and custom field IDs
- **`references/team-gitlab-mapping.md`** - GitLab group/project mapping per team (must be configured by user)
