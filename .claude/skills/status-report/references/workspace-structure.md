# ClickUp Workspace Structure Reference

## Workspace

- **Breeze Airways** - Workspace/Team ID: `2277049`

## Product Teams and Sprint Folders

Each product team has a space in ClickUp with sprint folders containing lists per sprint. Sprint lists follow a biweekly cadence. Below is the mapping of each product team to its sprint folder(s).

### SRE
- **Space ID:** `14826235`
- **2026 Sprint Folder ID:** `90147510422`
- **2025 Sprint Folder ID:** `90143945329`
- **2026 Retro Folder ID:** `90147510468`
- **Backlog Folder ID:** `90140228257` (Main Backlog list: `901400443388`)
- **Epics Folder ID:** `90140242642` (SRE Epics list: `901400480348`)
- Sprint naming: `Sprint N (MM/DD - MM/DD)`

### Operations
- **Space ID:** `12799086`
- **2026 Sprint Folder ID:** `90147563534`
- **2025 Sprint Folder ID:** `90144049601`
- **Epics Folder ID:** `120290296` (Operation's Backlog: `80047745`, Ops Platform Epics, Technical Debt, Postmortems)
- Sprint naming: `Sprint N (MM/DD - MM/DD)`

### Operations Systems
- **Space ID:** `90142455179`
- **Sprint Folder ID:** `90144086797`
- **Backlog Folder ID:** `90143926491` (Sys Ops Epics: `901406870416`)
- Sprint naming: `Sprint N (MM/DD - MM/DD)`

### Trip Services
- **Space ID:** `63124226`
- **Sprint Folder (called "Draws") ID:** `90144315292`
- **Product Folder ID:** `90144693306` (Requests: `901409257000`)
- Sprint naming: `Services N (MM/DD - MM/DD)`
- Additional lists: Quests (`901408374163`), Library (`901413878778`)

### Sell
- **Space ID:** `63124841`
- **2026 Sprint Folder ID:** `90147465093`
- **2025 Sprint Folder ID:** `90143928392`
- Sprint naming: `Sprint N (MM/DD - MM/DD)`
- Additional: Sell Backlog (`387164741`), Sell Opportunity Backlog (`900600494116`), Automation Epics (`90141823709`)

### Testing / QA
- **Space ID:** `12891104`
- **Sprint Folder ID:** `90140225326`
- Sprint naming: `Sprint N (MM/DD - MM/DD)` (numbering is cumulative, e.g., Sprint 62)

### Loyalty Experience (AirborneUnicorn)
- **Space ID:** `90140642974` (also accessible via `90142404391`)
- **2026 Sprint Folder ID:** `90147456951`
- **2025 Sprint Folder ID:** `90144062682`
- Sprint naming: Uses themed names like `Avada Kedavra 3 (MM/DD - MM/DD)`, `Dobby 2`, etc.
- Additional: LX Backlog (`901401867763`), Tech Roadmap folder (`90147027054`)

### Staff (Leadership)
- **Space ID:** `60289850`
- No traditional sprints; uses quarterly folders
- **Quarters Folder ID:** `90144455653`
  - 26Q1: `901414024744`
  - 25Q4: `901412964618`
- **Backlogs Folder ID:** `90144455654` (Initiatives: `901408538422`, Work: `901408141078`)

### Analytics & Optimization
- **Space ID:** `90140092278`
- No sprint folders; uses standing lists
- Data Collection (`901400234198`), Hypothesis Library (`901400234240`), Experiments (`901400234243`)

### AI
- **Space ID:** `90141866020`
- No sprint folders
- AI Guild Topics (`901404832595`), BYOAI (`901413463070`)

## Sprint Cadence

Sprints are biweekly across all teams. Most teams align to the same two-week windows. The typical pattern for 2026:
- Sprint 1: 1/1 - 1/14
- Sprint 2: 1/15 - 1/28
- Sprint 3: 1/29 - 2/11
- Sprint 4: 2/12 - 2/25
- Sprint 5: 2/26 - 3/11
- (continues biweekly)

## Task Statuses

Common statuses across spaces (may vary by team):
- **Open** / **To Do** - Not started
- **In Progress** / **In Dev** - Actively being worked on
- **In Review** / **Review** - Code review or stakeholder review
- **Closed** / **Complete** / **Done** - Finished
- **Blocked** - Waiting on dependency

## Important Notes

- Operations Systems often has 0-task sprints; include only if tasks exist.
- Testing/QA uses cumulative sprint numbering (e.g., Sprint 62 instead of Sprint 3).
- Loyalty Experience uses creative sprint theme names; match by date range, not sprint number.
- Trip Services calls sprints "Draws" and sprint lists "Services N".
- Staff space tracks quarterly initiatives, not sprints. Include if relevant to leadership visibility.
