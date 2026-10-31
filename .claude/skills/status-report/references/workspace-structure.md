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

### Field Ops
- **Space ID:** `12799086` (formerly "Operations" — renamed when the team split 2026-09-02)
- **2026 Sprint Folder ID:** `90147563534` (name: "Sprints 2026")
- **2025 Sprint Folder ID:** `90144049601`
- **Epics Folder ID:** `120290296`
  - Field Ops Backlog list: `80047745` (859 tasks as of 2026-09)
  - Field Ops Epics list: `900601272813`
  - Also in this folder: Technical Debt (`900601878184`), Postmortems (`901410000293`), Parking Lot (`901412744069`), 2026 Hackathon (`901414049448`)
- **Archives Folder ID:** `90144448816`
- **Risks Folder ID:** `90143602256` (Risks list: `901406077596`)
- Sprint naming: `Sprint N (MM/DD - MM/DD)`
- **Sprint list membership is unreliable** — see `status-report` SKILL.md Step 2a. Real sprint work is mostly subtasks multi-homed in from Backlog/Epics; `get_tasks` on the sprint list itself returns only a small fraction of the list's true `task_count`. Use the Backlog/Epics workaround, not the sprint list.

### Central Ops
- **Space ID:** `90147134052` (new space, split off from "Operations" 2026-09-02)
- **Sprint Folder ID:** `901411992361` (name: "2026 Sprints" — note reversed word order vs. Field Ops's "Sprints 2026")
- **Epics Folder ID:** `901411633495`
  - Central Ops Backlog list: `901419180254`
  - Central Ops Epics list: `901419180255`
  - Also in this folder: Technical Debt (`901419180256`), Postmortems (`901419180257`), Parking Lot (`901419180258`)
- **Archives Folder ID:** `901411633490`
- **Risks Folder ID:** `901411633496` (Risks list: `901419180261`)
- Sprint naming: `Sprint N (MM/DD - MM/DD)`
- **Sprint list membership is unreliable** — same issue as Field Ops. Central Ops Sprint 18 list metadata reports `task_count: 12` but `get_tasks` on that list returns only 2. Use the Backlog/Epics workaround (SKILL.md Step 2a), not the sprint list.

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
- Field Ops and Central Ops sprint lists cannot be trusted for task enumeration — use the Backlog/Epics workaround (SKILL.md Step 2a) for both.
- Staff space tracks quarterly initiatives, not sprints. Include if relevant to leadership visibility.
