---
name: status-report
description: This skill should be used when the user asks to "generate a status report", "create a sprint summary", "what happened last sprint", "sprint status", "status report", "sprint report", or discusses summarizing recent sprint work across teams
version: 1.0.0
---

# Sprint Status Report Generator

## Overview

Generate a comprehensive status report covering the last two sprints from the Breeze Airways ClickUp workspace. The report summarizes completed and in-progress work organized by product team, and highlights updates that may impact other teams.

## Workspace Context

The Breeze Airways ClickUp workspace (Team ID: `2277049`) contains multiple product teams, each with their own space and sprint folders. Refer to **`references/workspace-structure.md`** for the complete mapping of space IDs, sprint folder IDs, and naming conventions.

## Procedure

### Step 1: Select Report Scope

Before gathering any data, prompt the user to select which team(s) to include in the report. Use the `AskUserQuestion` tool with the following options:

- **SRE**
- **Operations**
- **Operations Systems**
- **Trip Services**
- **Sell**
- **Testing / QA**
- **Loyalty Experience**
- **All Teams** (generates a full cross-team report)

Wait for the user's selection before proceeding. The selected scope determines which teams to query in subsequent steps. If the user selects "All Teams", include every team listed above. If the user selects a single team, only query and report on that team.

### Step 2: Identify the Current and Previous Sprint

Determine today's date and calculate which two sprints to report on. Sprints are biweekly starting January 1, 2026. The "last 2 sprints" means the **current sprint** and the **sprint immediately before it**.

Use the sprint folder for the selected team(s) to list available sprint lists via `get_lists` with the appropriate folder ID. Identify the two most recent sprint lists by name or date range.

### Step 3: Gather Tasks

For each selected team, retrieve tasks from the last two sprint lists using `get_tasks`. Include closed/completed tasks by setting `include_closed: true`.

**Team sprint folder reference (2026 folder IDs):**

| Team | Sprint Folder ID | Notes |
|------|-----------------|-------|
| SRE | `90147510422` | Standard sprint naming |
| Operations | `90147563534` | Standard sprint naming |
| Operations Systems | `90144086797` | May have empty sprints; skip if 0 tasks |
| Trip Services | `90144315292` | Called "Draws"; lists named "Services N" |
| Sell | `90147465093` | Standard sprint naming |
| Testing / QA | `90140225326` | Cumulative numbering (e.g., Sprint 62) |
| Loyalty Experience | `90147456951` | Themed names (e.g., "Avada Kedavra 3") |

Only query teams matching the user's selection from Step 1. For each sprint list, call `get_tasks` with `include_closed: true` to capture both completed and active work. If a list has many tasks, paginate using the `page` parameter.

### Step 4: Enrich Task Details Where Needed

For tasks that appear to have cross-team impact or are high priority, use `get_task` to retrieve full details including the markdown description. Look for:
- Tasks mentioning other team names (SRE, Ops, Sell, Trip Services, Loyalty, etc.)
- Tasks related to shared infrastructure, APIs, databases, or deployment pipelines
- Tasks tagged as blockers or with dependencies on other teams
- Tasks involving migrations, schema changes, or breaking changes
- Tasks related to third-party integrations or vendor changes

### Step 5: Classify Each Task

For every task, record:
- **Task name and ID**
- **Status** (completed, in progress, blocked, open)
- **Assignee(s)**
- **Sprint** (current or previous)
- **Cross-team impact flag** (yes/no, with brief explanation if yes)

Group tasks into these categories:
1. **Completed** - Status is Closed, Complete, or Done
2. **In Progress** - Status is In Progress, In Dev, or In Review
3. **Blocked / At Risk** - Status is Blocked, or task has unresolved dependencies
4. **Planned / Not Started** - Status is Open or To Do

### Step 6: Identify Cross-Team Impacts

Flag any work that may affect other teams. Common patterns to watch for:
- **Infrastructure changes** (SRE) - deployment pipeline updates, environment changes, AWS migrations
- **API changes** (any team) - new endpoints, breaking changes, deprecations
- **Database/schema changes** - migrations that touch shared data
- **Shared service updates** (Operations) - changes to core platform services
- **Payment/booking flow changes** (Sell) - modifications to revenue-critical paths
- **Loyalty program changes** (Loyalty Experience) - point structures, partner integrations
- **Trip management changes** (Trip Services) - booking, check-in, or disruption handling
- **Test infrastructure changes** (Testing/QA) - test environment or automation updates

### Step 7: Generate the Report

Format the report using the structure below. When a single team is selected, omit the Key Metrics summary table and the "Team Reports" wrapper heading -- just show that team's section directly. When "All Teams" is selected, use the full multi-team format.

---

## Report Template

```
# Sprint Status Report
**Report Date:** [today's date]
**Sprints Covered:** [Previous Sprint Name (dates)] and [Current Sprint Name (dates)]
**Scope:** [Selected team name, or "All Teams"]

---

## Executive Summary

[2-3 sentences summarizing the overall state: how many tasks completed vs. in progress across all teams, any major milestones hit, and any significant blockers or risks.]

---

## Cross-Team Impact Alerts

> [List items that other teams need to be aware of. Each alert should name the originating team, describe the change, and call out which teams are affected.]

- **[Originating Team]**: [Description of change] - *Impacts: [affected teams]*
- ...

---

## Team Reports

### SRE

**Previous Sprint: [Sprint Name (dates)]**
| Status | Count |
|--------|-------|
| Completed | N |
| In Progress | N |
| Blocked | N |

**Completed Work:**
- [Task name] ([assignee]) - [one-line summary]
- ...

**In Progress:**
- [Task name] ([assignee]) - [one-line summary and current state]
- ...

**Blocked / At Risk:**
- [Task name] ([assignee]) - [blocker description]
- ...

**Current Sprint: [Sprint Name (dates)]**
[Same format as above]

---

### Operations
[Same format]

### Trip Services
[Same format]

### Sell
[Same format]

### Loyalty Experience
[Same format]

### Testing / QA
[Same format]

### Operations Systems
[Include only if tasks exist in the sprint period]

---

## Key Metrics

| Team | Completed (2 sprints) | In Progress | Blocked |
|------|----------------------|-------------|---------|
| SRE | N | N | N |
| Operations | N | N | N |
| Trip Services | N | N | N |
| Sell | N | N | N |
| Loyalty Experience | N | N | N |
| Testing / QA | N | N | N |
| **Total** | **N** | **N** | **N** |
```

## Execution Guidelines

- Always begin with the interactive team selection in Step 1. Do not skip this prompt.
- When "All Teams" is selected, maximize parallel tool calls: fetch sprint lists for all teams simultaneously, then fetch tasks for all lists simultaneously.
- When a single team is selected, only query that team's sprint folder. Still include the Cross-Team Impact Alerts section -- flag any tasks from that team that may affect other teams.
- When a team's sprint list has 0 tasks, skip it in the report rather than showing an empty section.
- If task names are cryptic, use `get_task` to read the description for a better summary.
- Keep task summaries to one line. Focus on *what* was accomplished or *what* is being worked on, not implementation details.
- For cross-team impacts, be specific about *what* changed and *who* is affected. Vague alerts are not actionable.
- If a task is blocked, explain *why* and *what* would unblock it if that information is available.
- Sort completed work by importance/impact, not alphabetically.
- Include assignee names so readers know who to contact for questions.

## Additional Resources

### Reference Files
- **`references/workspace-structure.md`** - Complete workspace hierarchy with all space IDs, folder IDs, list IDs, and naming conventions for every product team
