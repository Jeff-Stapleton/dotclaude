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
- Sprint naming: `Sprint N (MM/DD - MM/DD)`

### SRE
- **Space ID:** `14826235`
- **2026 Sprint Folder ID:** `90147510422`
- Sprint naming: `Sprint N (MM/DD - MM/DD)`

### Operations Systems
- **Space ID:** `90142455179`
- **Sprint Folder ID:** `90144086797`
- Sprint naming: `Sprint N (MM/DD - MM/DD)`

### Trip Services
- **Space ID:** `63124226`
- **Sprint Folder (called "Draws") ID:** `90144315292`
- Sprint naming: `Services N (MM/DD - MM/DD)`

## Sprint Cadence

Sprints are biweekly across all teams. 2026 pattern:
- Sprint 1: 1/1 - 1/14
- Sprint 2: 1/15 - 1/28
- Sprint 3: 1/29 - 2/11
- Sprint 4: 2/12 - 2/25
- Sprint 5: 2/26 - 3/11
- Sprint 6: 3/12 - 3/25
- Sprint 7: 3/26 - 4/8
- (continues biweekly — each sprint is 14 days)

## Task Architecture

Tasks live primarily in the **Epics list** or **Backlog list**. They are associated with sprint lists via ClickUp's **secondary locations** feature. The `get_tasks` API only returns tasks whose primary list is the sprint — to see all tasks in a sprint, use the `clickup_search` tool filtered by the sprint list as a subcategory location.

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

## Task Statuses Considered "Incomplete" (eligible for rollover)

Use prefix matching (case-insensitive). Roll over any task whose status starts with:
- `todo`
- `in progress`
- `specing`
- `code review`
- `product review`

Note: Only roll over `todo` and `in progress` by default. Ask the user if they also want `code review`, `product review`, and `specing` tasks.

## Task Statuses Considered "Done" (do NOT roll over)

- `done` (including `done (prod)`)
- `complete`
- `closed`
- `merged`

## View Configuration

The standard sprint list view uses these settings:
- **Visible columns:** assignee, pointsEstimate (with sum calculation), status, Task Type, Unplanned
- **Grouped by:** Team custom field
- **Hidden:** All other columns

### Custom Field IDs for View Columns
- Task Type: `cf_721ae2d2-9979-4956-9cfa-d92f2ac06238`
- Unplanned: `cf_41395f7f-62fd-4683-a396-757f91653239`
- Team (grouping): `cf_ebbcffe8-2615-42b9-802f-885d47206a07`
