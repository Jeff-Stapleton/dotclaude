# ClickUp Workspace Structure Reference — Sprint Planning

## Workspace

- **Breeze Airways** - Workspace/Team ID: `2277049`

## Product Teams, Sprint Folders, and Epics

### Operations
- **Space ID:** `12799086`
- **2026 Sprint Folder ID:** `90147563534`
- **2025 Sprint Folder ID:** `90144049601`
- **Epics List ID:** `900601272813` (Operation's Epics — stack ranked by priority via orderindex)
- **Backlog List ID:** `80047745` (Operation's Backlog)
- **Technical Debt List ID:** `900601878184`
- Sprint naming: `Sprint N (M/D - M/D)`

### SRE
- **Space ID:** `14826235`
- **2026 Sprint Folder ID:** `90147510422`
- Sprint naming: `Sprint N (M/D - M/D)`

### Operations Systems
- **Space ID:** `90142455179`
- **Sprint Folder ID:** `90144086797`
- Sprint naming: `Sprint N (M/D - M/D)`

### Trip Services
- **Space ID:** `63124226`
- **Sprint Folder (called "Draws") ID:** `90144315292`
- Sprint naming: `Services N (M/D - M/D)`

## Sprint Cadence

Sprints are biweekly across all teams. 2026 pattern:
- Sprint 1: 1/1 - 1/14
- Sprint 2: 1/15 - 1/28
- Sprint 3: 1/29 - 2/11
- Sprint 4: 2/12 - 2/25
- Sprint 5: 2/26 - 3/11
- Sprint 6: 3/12 - 3/25
- Sprint 7: 3/26 - 4/8
- Sprint 8: 4/9 - 4/22
- Sprint 9: 4/23 - 5/6
- (continues biweekly — each sprint is 14 days)

## Sprint Creation

**Sprints CANNOT be created via the ClickUp API.** The API only creates regular lists, which have the wrong entity type (different icon, missing sprint-specific behavior). Sprints must be created:
1. **Via Sprint Automations** (preferred) — ClickUp auto-creates the next sprint when the current one is marked done
2. **Manually in the UI** — click "Create Sprint" in the sprint folder

The sprint-planning skill assumes the target sprint already exists.

## Task Architecture

Tasks live primarily in the **Epics list** or **Backlog list**. They are associated with sprint lists via ClickUp's **secondary locations** feature.

### Finding Tasks in Sprints

- **`get_tasks`** (basic MCP) — returns EMPTY for sprint lists. Only finds tasks whose primary list is the sprint.
- **`search_tasks`** (basic MCP) with `list_ids` — also returns EMPTY for secondary-location tasks.
- **`clickup_search`** (claude_ai_ClickUp MCP) with `location.subcategories` — **THIS WORKS.** Finds all tasks including those added via secondary locations.

Example:
```
clickup_search(
  filters: {
    asset_types: ["task"],
    location: { subcategories: ["<sprint_list_id>"] }
  },
  count: 100
)
```

**Warning:** The `task_statuses` filter on `clickup_search` does NOT work — it returns all statuses regardless. Always filter statuses client-side.

## Custom Field IDs

### Team (dropdown) — used for grouping
- **Field ID:** `ebbcffe8-2615-42b9-802f-885d47206a07`
- Options: Product (0), Platform (1), On Deck (2)

### Task Type (dropdown)
- **Field ID:** `721ae2d2-9979-4956-9cfa-d92f2ac06238`
- Options: New Feature (0), Bug (1), Tech Debt (2), Enhancement (3), Automation (4), Security (5), DevOps (6), UI/UX (7), Epic (8), Docs/training (9), Suggestion (10), New Report (11), 20% Project (12), Easter Egg (13), Rebuild (14), Testing (15), Analytics (16)

### Unplanned (dropdown)
- **Field ID:** `41395f7f-62fd-4683-a396-757f91653239`
- Options: Planned (0), Unplanned (1), TODO is all blocked (2), On-Call Backlog (3)

### Setting Custom Fields via API
```bash
curl -s -X POST "https://api.clickup.com/api/v2/task/{task_id}/field/{field_id}" \
  -H "Authorization: ${CLICKUP_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"value": <option_index>}'
```

### Checking Custom Field Values via API
```bash
curl -s "https://api.clickup.com/api/v2/task/{task_id}?custom_fields=true" \
  -H "Authorization: ${CLICKUP_API_TOKEN}"
```
A field with `"value": null` means it is undefined/not set.

## Task Statuses — Rollover Rules

Roll over any task whose status is NOT in the "done" group:

**Roll over (incomplete):**
- `specing`
- `unrefined`
- `todo`
- `in progress`
- `code review`
- `product review`
- `awaiting release`

**Do NOT roll over (complete):**
- `Closed`
- `done (prod)`

## View Configuration

### Default View ID Pattern
The default "List" view for any sprint has ID: `6-{list_id}-1`

### Updating the Default View
**CRITICAL:** You must include `"name": "List"` and `"type": "list"` in the PUT payload. Without them the API returns VIEWS_055 or VIEWS_015 errors.

The default view is **lazily initialized** — it only exists after someone opens the sprint in the ClickUp UI. If the view returns "not found", ask the user to open the sprint first.

### Standard Sprint View Settings
- **Grouped by:** Team custom field
- **Visible columns:** assignee, dueDate, pointsEstimate (with sum calculation), status, Task Type, Unplanned
- **Hidden:** priority, name, id, customId, dates, sprints, Team field itself, all other fields
- **Settings:** show_subtasks=1, show_sprint_cards enabled

### Custom Field IDs for View Columns
- Task Type: `cf_721ae2d2-9979-4956-9cfa-d92f2ac06238`
- Unplanned: `cf_41395f7f-62fd-4683-a396-757f91653239`
- Team (grouping): `cf_ebbcffe8-2615-42b9-802f-885d47206a07`
