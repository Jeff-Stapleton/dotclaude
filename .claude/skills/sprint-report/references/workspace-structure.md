# ClickUp Workspace Structure Reference

## Workspace

- **Breeze Airways** - Workspace/Team ID: `2277049`

## Product Teams and Sprint Folders

Each product team has a space in ClickUp with sprint folders containing lists per sprint. Sprint lists follow a biweekly cadence.

### SRE
- **Space ID:** `14826235`
- **2026 Sprint Folder ID:** `90147510422`
- **2025 Sprint Folder ID:** `90143945329`
- Sprint naming: `Sprint N (MM/DD - MM/DD)`

### Operations
- **Space ID:** `12799086`
- **2026 Sprint Folder ID:** `90147563534`
- **2025 Sprint Folder ID:** `90144049601`
- Sprint naming: `Sprint N (MM/DD - MM/DD)`

### Operations Systems
- **Space ID:** `90142455179`
- **Sprint Folder ID:** `90144086797`
- Sprint naming: `Sprint N (MM/DD - MM/DD)`

### Trip Services
- **Space ID:** `63124226`
- **Sprint Folder (called "Draws") ID:** `90144315292`
- Sprint naming: `Services N (MM/DD - MM/DD)`

### Sell
- **Space ID:** `63124841`
- **2026 Sprint Folder ID:** `90147465093`
- **2025 Sprint Folder ID:** `90143928392`
- Sprint naming: `Sprint N (MM/DD - MM/DD)`

### Testing / QA
- **Space ID:** `12891104`
- **Sprint Folder ID:** `90140225326`
- Sprint naming: `Sprint N (MM/DD - MM/DD)` (cumulative numbering, e.g., Sprint 62)

### Loyalty Experience
- **Space ID:** `90140642974`
- **2026 Sprint Folder ID:** `90147456951`
- **2025 Sprint Folder ID:** `90144062682`
- Sprint naming: Uses themed names like `Hedwig 4 (MM/DD - MM/DD)`

## Sprint Cadence

Sprints are biweekly across all teams. 2026 pattern:
- Sprint 1: 1/1 - 1/14
- Sprint 2: 1/15 - 1/28
- Sprint 3: 1/29 - 2/11
- Sprint 4: 2/12 - 2/25
- Sprint 5: 2/26 - 3/11
- (continues biweekly)

## Task Statuses Considered "Completed"

Use **prefix matching** (startsWith) since teams append qualifiers like `done (prod)`:
- done
- complete
- closed
- merged

## Custom Fields for Metrics

### Task Type (dropdown)
- **Field ID:** `721ae2d2-9979-4956-9cfa-d92f2ac06238`
- All options: New Feature (0), Bug (1), Tech Debt (2), Enhancement (3), Automation (4), Security (5), DevOps (6), UI/UX (7), Epic (8), Docs/training (9), Suggestion (10), New Report (11), 20% Project (12), Easter Egg (13), Rebuild (14), Testing (15), Analytics (16)
- Key types for metrics:
  - **Bug** (index 1)
  - **Tech Debt** (index 2) - counts as Maintenance
  - **Security** (index 5) - counts as Maintenance

### Unplanned (dropdown)
- **Field ID:** `41395f7f-62fd-4683-a396-757f91653239`
- Options: Planned (0), **Unplanned (1)**, TODO is all blocked (2), On-Call Backlog (3)
- A task is "unplanned" when the dropdown value is `1`
