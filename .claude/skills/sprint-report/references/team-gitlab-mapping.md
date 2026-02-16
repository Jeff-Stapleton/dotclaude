# Team to GitLab Group/Project Mapping

This file maps ClickUp teams to their GitLab groups or projects for MR calculations.
Update these mappings as teams and repos change.

## Configuration

- **GitLab Host:** `gitlab.com`
- **Top-level Group:** `breeze-airways`
- The `glab` CLI must be authenticated. Run `glab auth login` to set up.

## Team Mappings

Each team maps to one or more GitLab groups. The skill queries all groups for a team
to calculate total merged MRs during the sprint period.

| Team | GitLab Groups/Projects | Notes |
|------|----------------------|-------|
| SRE | `breeze-airways/sre` | TODO: verify path |
| Operations | `breeze-airways/operations` | Confirmed |
| Operations Systems | `breeze-airways/operations-systems` | TODO: verify path |
| Trip Services | `breeze-airways/trip-services` | TODO: verify path |
| Sell | `breeze-airways/sell` | TODO: verify path |
| Testing / QA | `breeze-airways/testing` | TODO: verify path |
| Loyalty Experience | `breeze-airways/loyalty-experience` | TODO: verify path |

## How MRs Are Queried

For each GitLab group, the skill runs:
```bash
glab mr list --group <group-path> --state merged --after=<sprint-start> --before=<sprint-end> --per-page=100
```

The total count is divided by the number of working days in the sprint (typically 10 for a 2-week sprint).
