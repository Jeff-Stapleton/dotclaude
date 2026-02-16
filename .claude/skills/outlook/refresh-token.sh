#!/bin/bash

# Outlook Token Refresh Script
# Use this to refresh your access token when it expires (every hour)

echo "========================================"
echo "Outlook Token Refresh"
echo "========================================"
echo ""

if [ -z "$OUTLOOK_CLIENT_ID" ]; then
    echo "Error: OUTLOOK_CLIENT_ID not set"
    echo "Please set it in your environment or run auth-helper.sh first"
    exit 1
fi

if [ -z "$OUTLOOK_REFRESH_TOKEN" ]; then
    echo "Error: OUTLOOK_REFRESH_TOKEN not set"
    echo "Please run auth-helper.sh first to get your refresh token"
    exit 1
fi

echo "Refreshing access token..."
echo ""

TENANT_ID="common"
SCOPE="https://graph.microsoft.com/Mail.Read https://graph.microsoft.com/User.Read offline_access"

TOKEN_RESPONSE=$(curl -s -X POST "https://login.microsoftonline.com/$TENANT_ID/oauth2/v2.0/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "client_id=$OUTLOOK_CLIENT_ID&grant_type=refresh_token&refresh_token=$OUTLOOK_REFRESH_TOKEN&scope=$SCOPE")

ACCESS_TOKEN=$(echo "$TOKEN_RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
NEW_REFRESH_TOKEN=$(echo "$TOKEN_RESPONSE" | grep -o '"refresh_token":"[^"]*"' | cut -d'"' -f4)

if [ ! -z "$ACCESS_TOKEN" ]; then
    echo "Success! Token refreshed."
    echo ""
    echo "========================================"
    echo "Run these commands:"
    echo "========================================"
    echo ""
    echo "export OUTLOOK_ACCESS_TOKEN=\"$ACCESS_TOKEN\""
    if [ ! -z "$NEW_REFRESH_TOKEN" ]; then
        echo "export OUTLOOK_REFRESH_TOKEN=\"$NEW_REFRESH_TOKEN\""
    fi
    echo ""
    echo "Also update these in your shell profile (~/.zshrc or ~/.bashrc)"
else
    ERROR=$(echo "$TOKEN_RESPONSE" | grep -o '"error":"[^"]*"' | cut -d'"' -f4)
    ERROR_DESC=$(echo "$TOKEN_RESPONSE" | grep -o '"error_description":"[^"]*"' | cut -d'"' -f4)
    echo "Error: $ERROR"
    echo "Description: $ERROR_DESC"
    echo ""
    echo "You may need to re-authenticate using auth-helper.sh"
    exit 1
fi
