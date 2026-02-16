#!/bin/bash

# Outlook Authentication Helper Script
# This script helps you authenticate with Microsoft Graph API to access Outlook emails

echo "========================================"
echo "Outlook Authentication Helper"
echo "========================================"
echo ""

# Check if CLIENT_ID is already set
if [ -z "$OUTLOOK_CLIENT_ID" ]; then
    echo "Step 1: Enter your Azure App Client ID"
    echo "If you haven't registered an app yet, follow these steps:"
    echo "1. Go to https://portal.azure.com/#blade/Microsoft_AAD_RegisteredApps/ApplicationsListBlade"
    echo "2. Click 'New registration'"
    echo "3. Name: 'Claude Outlook Integration'"
    echo "4. Supported account types: 'Accounts in any organizational directory and personal Microsoft accounts'"
    echo "5. Redirect URI: https://login.microsoftonline.com/common/oauth2/nativeclient (Public client/native)"
    echo "6. Click 'Register' and copy the Application (client) ID"
    echo ""
    read -p "Enter your Client ID: " CLIENT_ID
else
    CLIENT_ID="$OUTLOOK_CLIENT_ID"
    echo "Using CLIENT_ID from environment: $CLIENT_ID"
fi

echo ""
echo "Step 2: Requesting device code..."
echo ""

TENANT_ID="05fbf8f1-b0b0-4267-b065-30f37c6a5aac"
SCOPE="https://graph.microsoft.com/Mail.Read https://graph.microsoft.com/User.Read offline_access"

# Request device code
RESPONSE=$(curl -s -X POST "https://login.microsoftonline.com/$TENANT_ID/oauth2/v2.0/devicecode" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "client_id=$CLIENT_ID&scope=$SCOPE")

# Extract values
USER_CODE=$(echo "$RESPONSE" | grep -o '"user_code":"[^"]*"' | cut -d'"' -f4)
DEVICE_CODE=$(echo "$RESPONSE" | grep -o '"device_code":"[^"]*"' | cut -d'"' -f4)
VERIFICATION_URI=$(echo "$RESPONSE" | grep -o '"verification_uri":"[^"]*"' | cut -d'"' -f4)
MESSAGE=$(echo "$RESPONSE" | grep -o '"message":"[^"]*"' | sed 's/"message":"//; s/"$//')

if [ -z "$USER_CODE" ]; then
    echo "Error: Failed to get device code"
    echo "Response: $RESPONSE"
    exit 1
fi

echo "========================================"
echo "ACTION REQUIRED:"
echo "========================================"
echo "$MESSAGE"
echo ""
echo "User Code: $USER_CODE"
echo "Verification URL: $VERIFICATION_URI"
echo ""
echo "Press Enter after you've completed the authentication in your browser..."
read

echo ""
echo "Waiting for authentication to complete..."
echo ""

# Poll for token (try up to 10 times, 5 seconds apart)
for i in {1..10}; do
    TOKEN_RESPONSE=$(curl -s -X POST "https://login.microsoftonline.com/$TENANT_ID/oauth2/v2.0/token" \
      -H "Content-Type: application/x-www-form-urlencoded" \
      -d "client_id=$CLIENT_ID&grant_type=urn:ietf:params:oauth:grant-type:device_code&device_code=$DEVICE_CODE")

    ACCESS_TOKEN=$(echo "$TOKEN_RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
    REFRESH_TOKEN=$(echo "$TOKEN_RESPONSE" | grep -o '"refresh_token":"[^"]*"' | cut -d'"' -f4)

    if [ ! -z "$ACCESS_TOKEN" ]; then
        echo "Success! Authentication complete."
        echo ""
        echo "========================================"
        echo "Add these to your shell profile (~/.zshrc or ~/.bashrc):"
        echo "========================================"
        echo ""
        echo "export OUTLOOK_CLIENT_ID=\"$CLIENT_ID\""
        echo "export OUTLOOK_ACCESS_TOKEN=\"$ACCESS_TOKEN\""
        echo "export OUTLOOK_REFRESH_TOKEN=\"$REFRESH_TOKEN\""
        echo ""
        echo "For this session, run:"
        echo "========================================"
        echo "export OUTLOOK_CLIENT_ID=\"$CLIENT_ID\""
        echo "export OUTLOOK_ACCESS_TOKEN=\"$ACCESS_TOKEN\""
        echo "export OUTLOOK_REFRESH_TOKEN=\"$REFRESH_TOKEN\""
        echo ""
        echo "Note: Access token expires in 1 hour. Use the refresh token to get a new one."
        exit 0
    fi

    ERROR=$(echo "$TOKEN_RESPONSE" | grep -o '"error":"[^"]*"' | cut -d'"' -f4)
    if [ "$ERROR" = "authorization_pending" ]; then
        echo "Waiting... (attempt $i/10)"
        sleep 5
    else
        echo "Error: $ERROR"
        echo "Response: $TOKEN_RESPONSE"
        exit 1
    fi
done

echo "Timeout: Authentication not completed in time. Please run the script again."
exit 1
