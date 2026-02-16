---
name: outlook
description: "Read emails from Microsoft Outlook and identify urgent messages that need attention"
---

# Outlook Email Skill

Read and summarize emails from Microsoft Outlook using the Microsoft Graph API.

## Authentication

The access token is stored in the `OUTLOOK_ACCESS_TOKEN` environment variable. All requests must include the header:

```
Authorization: Bearer $OUTLOOK_ACCESS_TOKEN
```

## Base URL

```
https://graph.microsoft.com/v1.0
```

## Setup Instructions

### Getting Your Access Token

1. **Register an App in Azure AD** (One-time setup):
   - Go to https://portal.azure.com/#blade/Microsoft_AAD_RegisteredApps/ApplicationsListBlade
   - Click "New registration"
   - Name: "Claude Outlook Integration"
   - Supported account types: "Accounts in any organizational directory and personal Microsoft accounts"
   - Redirect URI: `https://login.microsoftonline.com/common/oauth2/nativeclient` (Public client/native)
   - Click "Register"
   - Note the **Application (client) ID**

2. **Configure API Permissions**:
   - In your app, go to "API permissions"
   - Click "Add a permission" → "Microsoft Graph" → "Delegated permissions"
   - Add these permissions:
     - `Mail.Read` - Read user mail
     - `Mail.ReadBasic` - Read basic mail info
     - `User.Read` - Sign in and read user profile
   - Click "Add permissions"

3. **Get Access Token** (Using Device Code Flow):

   ```bash
   # Step 1: Request device code
   TENANT_ID="common"
   CLIENT_ID="your-client-id-here"
   SCOPE="https://graph.microsoft.com/Mail.Read https://graph.microsoft.com/User.Read offline_access"

   curl -X POST "https://login.microsoftonline.com/$TENANT_ID/oauth2/v2.0/devicecode" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "client_id=$CLIENT_ID&scope=$SCOPE"
   ```

   This will return a `user_code` and `device_code`. Open the verification URL and enter the user code.

   ```bash
   # Step 2: Poll for token (after completing device authentication)
   DEVICE_CODE="device-code-from-step-1"

   curl -X POST "https://login.microsoftonline.com/$TENANT_ID/oauth2/v2.0/token" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "client_id=$CLIENT_ID&grant_type=urn:ietf:params:oauth:grant-type:device_code&device_code=$DEVICE_CODE"
   ```

   Save the `access_token` to your environment:

   ```bash
   export OUTLOOK_ACCESS_TOKEN="your-access-token-here"
   # Add to your ~/.zshrc or ~/.bashrc to persist
   ```

### Token Refresh

Tokens expire after 1 hour. Save the `refresh_token` and use it to get a new access token:

```bash
curl -X POST "https://login.microsoftonline.com/common/oauth2/v2.0/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "client_id=$CLIENT_ID&grant_type=refresh_token&refresh_token=$REFRESH_TOKEN&scope=$SCOPE"
```

## Reading Emails

### List Messages from Inbox

```bash
curl -s "https://graph.microsoft.com/v1.0/me/mailFolders/inbox/messages" \
  -H "Authorization: Bearer $OUTLOOK_ACCESS_TOKEN"
```

**Query Parameters:**
- `$top=N` - Limit number of messages (default: 10, max: 999)
- `$skip=N` - Skip N messages (pagination)
- `$select=field1,field2` - Select specific fields
- `$filter=` - Filter messages (e.g., `isRead eq false`)
- `$orderby=` - Sort messages (e.g., `receivedDateTime desc`)
- `$search="query"` - Search messages

**Common field selections:**
```
$select=id,subject,from,toRecipients,receivedDateTime,isRead,hasAttachments,bodyPreview,body
```

### List Unread Messages

```bash
curl -s "https://graph.microsoft.com/v1.0/me/mailFolders/inbox/messages?\$filter=isRead eq false&\$top=20" \
  -H "Authorization: Bearer $OUTLOOK_ACCESS_TOKEN"
```

### List Recent Messages

```bash
curl -s "https://graph.microsoft.com/v1.0/me/mailFolders/inbox/messages?\$orderby=receivedDateTime desc&\$top=10" \
  -H "Authorization: Bearer $OUTLOOK_ACCESS_TOKEN"
```

### Get a Specific Message

```bash
curl -s "https://graph.microsoft.com/v1.0/me/messages/{message_id}" \
  -H "Authorization: Bearer $OUTLOOK_ACCESS_TOKEN"
```

### Get Message Body as Plain Text

```bash
curl -s "https://graph.microsoft.com/v1.0/me/messages/{message_id}?\$select=body" \
  -H "Authorization: Bearer $OUTLOOK_ACCESS_TOKEN" \
  -H "Prefer: outlook.body-content-type='text'"
```

### Search Messages

```bash
# Search by keyword
curl -s "https://graph.microsoft.com/v1.0/me/messages?\$search=\"project update\"" \
  -H "Authorization: Bearer $OUTLOOK_ACCESS_TOKEN"

# Search from specific sender
curl -s "https://graph.microsoft.com/v1.0/me/messages?\$filter=from/emailAddress/address eq 'sender@example.com'" \
  -H "Authorization: Bearer $OUTLOOK_ACCESS_TOKEN"
```

### Mark as Read

```bash
curl -s -X PATCH "https://graph.microsoft.com/v1.0/me/messages/{message_id}" \
  -H "Authorization: Bearer $OUTLOOK_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"isRead": true}'
```

## Mail Folders

### List All Mail Folders

```bash
curl -s "https://graph.microsoft.com/v1.0/me/mailFolders" \
  -H "Authorization: Bearer $OUTLOOK_ACCESS_TOKEN"
```

### Common Folder Names
- `inbox` - Inbox folder
- `sentitems` - Sent Items
- `deleteditems` - Deleted Items
- `drafts` - Drafts
- `junkemail` - Junk Email

### Get Messages from Specific Folder

```bash
curl -s "https://graph.microsoft.com/v1.0/me/mailFolders/{folder_id}/messages" \
  -H "Authorization: Bearer $OUTLOOK_ACCESS_TOKEN"
```

## Attachments

### List Attachments

```bash
curl -s "https://graph.microsoft.com/v1.0/me/messages/{message_id}/attachments" \
  -H "Authorization: Bearer $OUTLOOK_ACCESS_TOKEN"
```

### Download Attachment

```bash
curl -s "https://graph.microsoft.com/v1.0/me/messages/{message_id}/attachments/{attachment_id}" \
  -H "Authorization: Bearer $OUTLOOK_ACCESS_TOKEN"
```

## Email Summarization Workflow

When asked to summarize emails, follow this workflow:

1. **List recent emails** with subject, sender, and preview:
   ```bash
   curl -s "https://graph.microsoft.com/v1.0/me/mailFolders/inbox/messages?\$top=20&\$orderby=receivedDateTime desc&\$select=id,subject,from,receivedDateTime,bodyPreview,isRead" \
     -H "Authorization: Bearer $OUTLOOK_ACCESS_TOKEN"
   ```

2. **For each email to summarize**, get the full body:
   ```bash
   curl -s "https://graph.microsoft.com/v1.0/me/messages/{message_id}?\$select=subject,from,receivedDateTime,body" \
     -H "Authorization: Bearer $OUTLOOK_ACCESS_TOKEN" \
     -H "Prefer: outlook.body-content-type='text'"
   ```

3. **Summarize** by:
   - Grouping by sender or topic
   - Highlighting important messages (from key people, with urgent keywords)
   - Extracting action items
   - Identifying unread messages

## Urgent Email Identification Workflow

When asked to identify urgent emails, find emails that need attention, or check for important messages, follow this workflow:

### Step 1: Fetch Recent Unread Emails

Get unread emails from the last 48 hours:

```bash
# Calculate datetime for 48 hours ago (ISO 8601 format)
SINCE=$(date -u -v-48H +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || date -u -d "48 hours ago" +"%Y-%m-%dT%H:%M:%SZ")

curl -s "https://graph.microsoft.com/v1.0/me/mailFolders/inbox/messages?\$filter=isRead eq false and receivedDateTime ge $SINCE&\$top=50&\$orderby=receivedDateTime desc&\$select=id,subject,from,receivedDateTime,bodyPreview,importance,hasAttachments" \
  -H "Authorization: Bearer $OUTLOOK_ACCESS_TOKEN"
```

### Step 2: AI-Powered Urgency Analysis

Analyze each email using these criteria to determine urgency:

**Sender Signals:**
- Executives, managers, or leadership (titles like CEO, VP, Director, Manager)
- External clients or partners
- IT/Security teams (potential incidents)
- HR (time-sensitive policies or requests)

**Subject Line Keywords:**
- URGENT, ASAP, ACTION REQUIRED, IMMEDIATE
- Deadline, EOD, COB, by end of day
- Response needed, Please respond, Waiting on
- Time-sensitive, Critical, Important
- FYI with your name mentioned

**Content Analysis:**
- Direct questions requiring your response
- Explicit requests for action or deliverables
- Escalations or follow-ups on previous requests
- Meeting requests with deadlines within 24 hours
- Mentions of your name or asks for your input specifically

**Importance Indicators:**
- `importance: "high"` flag set by sender
- `hasAttachments: true` combined with action keywords
- Short, direct emails (often more urgent than long ones)

**Recency Weighting:**
- Last 4 hours: Higher urgency
- Last 24 hours: Medium urgency boost
- 24-48 hours: Standard assessment

### Step 3: Categorize and Present Results

Present emails in priority order using these categories:

**CRITICAL** - Requires immediate attention:
- High importance flag + action keywords
- Sender is executive or external client with deadline
- Security/IT incidents
- Missed meeting or urgent follow-up

**IMPORTANT** - Should address today:
- Direct questions or requests for action
- Deadlines within 24-48 hours
- Follow-ups on items you own
- External communications

**REVIEW** - Worth checking when available:
- FYI emails that mention you
- Team updates you should be aware of
- Lower-priority requests

### Step 4: Offer Actions

After presenting the summary, offer to:
- Show the full content of any specific email
- Mark emails as read after review
- Search for related emails or threads

## Response Format

All responses are in JSON format. Key fields:

- `id` - Unique message ID
- `subject` - Email subject
- `from` - Sender information (`{ "emailAddress": { "name": "...", "address": "..." }}`)
- `toRecipients` - Array of recipients
- `receivedDateTime` - ISO 8601 timestamp
- `isRead` - Boolean
- `hasAttachments` - Boolean
- `bodyPreview` - First 255 characters of body
- `body` - Full email body (`{ "contentType": "html|text", "content": "..." }`)
- `importance` - "low", "normal", or "high"

## Error Handling

Common errors:
- `401 Unauthorized` - Token expired or invalid, refresh token
- `403 Forbidden` - Missing required permissions
- `404 Not Found` - Invalid message or folder ID
- `429 Too Many Requests` - Rate limited, wait and retry

## Rate Limits

- Microsoft Graph API has throttling limits
- For mail operations: typically 10,000 requests per 10 minutes per app per user
- If throttled (429 response), check `Retry-After` header

## Privacy & Security

- Access tokens grant access to user's email - handle securely
- Never log or expose access tokens
- Tokens should be stored in environment variables, not in code
- Use refresh tokens to get new access tokens when they expire
