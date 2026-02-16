---
name: clickup
description: Interface with ClickUp API to manage tasks, subtasks, and wiki docs. Use when the user wants to create, update, list, or delete ClickUp tasks, or manage ClickUp Docs/wikis.
---

# ClickUp API Skill

Manage ClickUp tasks and documents via the ClickUp API.

## Authentication

The API token is stored in the `CLICKUP_API_TOKEN` environment variable. All requests must include the header:

```
Authorization: $CLICKUP_API_TOKEN
```

## Base URL

```
https://api.clickup.com/api/v2
```

## Default Configuration

When no space is specified, always default to the **Operations** space:

- **Workspace/Team ID**: `2277049` (Breeze Airways)
- **Default Space ID**: `12799086` (Operations)

Use these defaults unless the user explicitly requests a different space.

## Task Management

### List Tasks in a List

```bash
curl -s "https://api.clickup.com/api/v2/list/{list_id}/task" \
  -H "Authorization: $CLICKUP_API_TOKEN"
```

### Get a Task

```bash
curl -s "https://api.clickup.com/api/v2/task/{task_id}" \
  -H "Authorization: $CLICKUP_API_TOKEN"
```

### Create a Task

```bash
curl -s -X POST "https://api.clickup.com/api/v2/list/{list_id}/task" \
  -H "Authorization: $CLICKUP_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Task Name",
    "description": "Task description",
    "status": "to do",
    "priority": 3,
    "due_date": 1234567890000,
    "assignees": [123456]
  }'
```

Priority values: 1 = urgent, 2 = high, 3 = normal, 4 = low

### Update a Task

```bash
curl -s -X PUT "https://api.clickup.com/api/v2/task/{task_id}" \
  -H "Authorization: $CLICKUP_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Name",
    "status": "in progress"
  }'
```

### Delete a Task

```bash
curl -s -X DELETE "https://api.clickup.com/api/v2/task/{task_id}" \
  -H "Authorization: $CLICKUP_API_TOKEN"
```

### Create a Subtask

```bash
curl -s -X POST "https://api.clickup.com/api/v2/list/{list_id}/task" \
  -H "Authorization: $CLICKUP_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Subtask Name",
    "parent": "{parent_task_id}"
  }'
```

### Add a Comment to a Task

```bash
curl -s -X POST "https://api.clickup.com/api/v2/task/{task_id}/comment" \
  -H "Authorization: $CLICKUP_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "comment_text": "Your comment here"
  }'
```

## Wiki / Docs Management

### List Docs in a Workspace

```bash
curl -s "https://api.clickup.com/api/v3/workspaces/{workspace_id}/docs" \
  -H "Authorization: $CLICKUP_API_TOKEN"
```

### Get a Doc

```bash
curl -s "https://api.clickup.com/api/v3/docs/{doc_id}" \
  -H "Authorization: $CLICKUP_API_TOKEN"
```

### Create a Doc

```bash
curl -s -X POST "https://api.clickup.com/api/v3/workspaces/{workspace_id}/docs" \
  -H "Authorization: $CLICKUP_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Doc Title",
    "parent": {
      "id": "{parent_id}",
      "type": 4
    }
  }'
```

Parent types: 4 = space, 5 = folder, 6 = list, 7 = everything level

### Get Doc Pages

```bash
curl -s "https://api.clickup.com/api/v3/docs/{doc_id}/pages" \
  -H "Authorization: $CLICKUP_API_TOKEN"
```

### Create a Page in a Doc

```bash
curl -s -X POST "https://api.clickup.com/api/v3/docs/{doc_id}/pages" \
  -H "Authorization: $CLICKUP_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Page Title",
    "content": "Page content in markdown"
  }'
```

### Update a Page

```bash
curl -s -X PUT "https://api.clickup.com/api/v3/docs/{doc_id}/pages/{page_id}" \
  -H "Authorization: $CLICKUP_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Title",
    "content": "Updated content"
  }'
```

## Workspace & Hierarchy Discovery

### Get Authorized Teams (Workspaces)

```bash
curl -s "https://api.clickup.com/api/v2/team" \
  -H "Authorization: $CLICKUP_API_TOKEN"
```

### Get Spaces in a Workspace

```bash
curl -s "https://api.clickup.com/api/v2/team/{team_id}/space" \
  -H "Authorization: $CLICKUP_API_TOKEN"
```

### Get Folders in a Space

```bash
curl -s "https://api.clickup.com/api/v2/space/{space_id}/folder" \
  -H "Authorization: $CLICKUP_API_TOKEN"
```

### Get Lists in a Folder

```bash
curl -s "https://api.clickup.com/api/v2/folder/{folder_id}/list" \
  -H "Authorization: $CLICKUP_API_TOKEN"
```

### Get Folderless Lists in a Space

```bash
curl -s "https://api.clickup.com/api/v2/space/{space_id}/list" \
  -H "Authorization: $CLICKUP_API_TOKEN"
```

## Git Branch Naming

When creating branches for ClickUp tasks, use only the task ID as the branch name:

- **Format**: `OPS-6417`
- **Do NOT** include the task name or description in the branch name

## Workflow

1. **Default to Operations**: Always use the Operations space (ID: `12799086`) unless the user specifies a different space
2. **Navigate hierarchy**: Space -> Folders -> Lists -> Tasks (skip team discovery since defaults are configured)
3. **Ask for IDs**: When the user doesn't provide required IDs (list_id, task_id, etc.), help them discover them via the hierarchy endpoints within the Operations space first
4. **Confirm destructive actions**: Always confirm before deleting tasks or docs

## Error Handling

If a request fails, check:
- Token validity: ensure `CLICKUP_API_TOKEN` is set
- ID correctness: workspace, space, folder, list, and task IDs must be valid
- Permissions: the token must have access to the requested resource
