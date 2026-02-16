---
name: gitlab
description: Interface with GitLab API to create branches and open merge requests. Use when the user wants to create feature branches, open MRs, or manage GitLab repository workflows.
---

# GitLab API Skill

Create branches and manage merge requests via the GitLab API.

## Authentication

The API token is stored in the `GITLAB_API_TOKEN` environment variable. All requests must include the header:

```
PRIVATE-TOKEN: $GITLAB_API_TOKEN
```

## Base URL

```
https://gitlab.com/api/v4
```

If using a self-hosted GitLab instance, replace `gitlab.com` with your instance URL.

## Default Configuration

When no group or project is specified, always default to the **Breeze Airways / operations** subgroup:

- **Default Group**: `breeze-airways`
- **Default Subgroup**: `breeze-airways/operations`
- **URL-encoded path**: `breeze-airways%2Foperations`

For projects within this subgroup, the full path would be: `breeze-airways/operations/{project-name}`

Use these defaults unless the user explicitly requests a different group or project.

## Project ID

GitLab API requires a project ID or URL-encoded project path. To find your project ID:

```bash
curl -s "https://gitlab.com/api/v4/projects?search=PROJECT_NAME" \
  -H "PRIVATE-TOKEN: $GITLAB_API_TOKEN"
```

Or use the URL-encoded path (e.g., `my-group%2Fmy-project` for `my-group/my-project`).

## Branch Management

### List Branches

```bash
curl -s "https://gitlab.com/api/v4/projects/{project_id}/repository/branches" \
  -H "PRIVATE-TOKEN: $GITLAB_API_TOKEN"
```

### Get a Branch

```bash
curl -s "https://gitlab.com/api/v4/projects/{project_id}/repository/branches/{branch_name}" \
  -H "PRIVATE-TOKEN: $GITLAB_API_TOKEN"
```

### Create a Branch

```bash
curl -s -X POST "https://gitlab.com/api/v4/projects/{project_id}/repository/branches" \
  -H "PRIVATE-TOKEN: $GITLAB_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "branch": "feature/new-branch-name",
    "ref": "main"
  }'
```

Parameters:
- `branch`: Name of the new branch
- `ref`: Branch name or commit SHA to create branch from

### Delete a Branch

```bash
curl -s -X DELETE "https://gitlab.com/api/v4/projects/{project_id}/repository/branches/{branch_name}" \
  -H "PRIVATE-TOKEN: $GITLAB_API_TOKEN"
```

## Merge Requests

### List Merge Requests

```bash
curl -s "https://gitlab.com/api/v4/projects/{project_id}/merge_requests?state=opened" \
  -H "PRIVATE-TOKEN: $GITLAB_API_TOKEN"
```

State options: `opened`, `closed`, `merged`, `all`

### Get a Merge Request

```bash
curl -s "https://gitlab.com/api/v4/projects/{project_id}/merge_requests/{mr_iid}" \
  -H "PRIVATE-TOKEN: $GITLAB_API_TOKEN"
```

### Create a Merge Request

```bash
curl -s -X POST "https://gitlab.com/api/v4/projects/{project_id}/merge_requests" \
  -H "PRIVATE-TOKEN: $GITLAB_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "source_branch": "feature/my-feature",
    "target_branch": "main",
    "title": "Add new feature",
    "description": "## Summary\n\nDescription of changes...\n\n## Test Plan\n\n- [ ] Unit tests added\n- [ ] Manual testing completed",
    "remove_source_branch": true,
    "squash": true
  }'
```

Parameters:
- `source_branch`: (required) Source branch name
- `target_branch`: (required) Target branch name
- `title`: (required) Title of the MR
- `description`: Description/body of the MR (supports markdown)
- `assignee_id`: User ID to assign
- `assignee_ids`: Array of user IDs for multiple assignees
- `reviewer_ids`: Array of user IDs to request review from
- `labels`: Comma-separated label names
- `milestone_id`: Milestone ID to associate
- `remove_source_branch`: Delete source branch when merged (default: false)
- `squash`: Squash commits when merged (default: false)
- `draft`: Create as draft/WIP MR (default: false)

### Update a Merge Request

```bash
curl -s -X PUT "https://gitlab.com/api/v4/projects/{project_id}/merge_requests/{mr_iid}" \
  -H "PRIVATE-TOKEN: $GITLAB_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated title",
    "description": "Updated description"
  }'
```

### Add a Comment to a Merge Request

```bash
curl -s -X POST "https://gitlab.com/api/v4/projects/{project_id}/merge_requests/{mr_iid}/notes" \
  -H "PRIVATE-TOKEN: $GITLAB_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "body": "Your comment here"
  }'
```

### Merge a Merge Request

```bash
curl -s -X PUT "https://gitlab.com/api/v4/projects/{project_id}/merge_requests/{mr_iid}/merge" \
  -H "PRIVATE-TOKEN: $GITLAB_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "squash": true,
    "should_remove_source_branch": true
  }'
```

## Users

### Get Current User

```bash
curl -s "https://gitlab.com/api/v4/user" \
  -H "PRIVATE-TOKEN: $GITLAB_API_TOKEN"
```

### Search Users

```bash
curl -s "https://gitlab.com/api/v4/users?search=username" \
  -H "PRIVATE-TOKEN: $GITLAB_API_TOKEN"
```

## Workflow

1. **Default to operations subgroup**: Always use `breeze-airways/operations` as the default subgroup unless the user specifies otherwise
2. **Get project ID**: If not known, search for the project within the operations subgroup first
3. **Create branch**: Create a feature branch from the target branch (usually `main`)
4. **Open MR**: After commits are pushed, create a merge request
5. **Confirm destructive actions**: Always confirm before deleting branches or merging MRs

## Error Handling

If a request fails, check:
- Token validity: ensure `GITLAB_API_TOKEN` is set and has appropriate scopes (`api` scope recommended)
- Project ID: must be numeric ID or URL-encoded path
- Branch names: must be URL-encoded if they contain special characters (use `jq -rn --arg b "branch/name" '$b | @uri'`)
- Permissions: the token must have access to the requested project
