#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_DIR="$HOME/.claude"

echo "Setting up Claude Code dotfiles..."

# Create ~/.claude if it doesn't exist
mkdir -p "$CLAUDE_DIR"

# Symlink settings.json
if [ -L "$CLAUDE_DIR/settings.json" ]; then
    echo "settings.json symlink already exists, replacing..."
    rm "$CLAUDE_DIR/settings.json"
elif [ -f "$CLAUDE_DIR/settings.json" ]; then
    echo "Backing up existing settings.json to settings.json.bak"
    mv "$CLAUDE_DIR/settings.json" "$CLAUDE_DIR/settings.json.bak"
fi
ln -s "$SCRIPT_DIR/.claude/settings.json" "$CLAUDE_DIR/settings.json"
echo "  Linked settings.json"

# Symlink skills directory
if [ -L "$CLAUDE_DIR/skills" ]; then
    echo "skills symlink already exists, replacing..."
    rm "$CLAUDE_DIR/skills"
elif [ -d "$CLAUDE_DIR/skills" ]; then
    echo "Backing up existing skills/ to skills.bak/"
    mv "$CLAUDE_DIR/skills" "$CLAUDE_DIR/skills.bak"
fi
ln -s "$SCRIPT_DIR/.claude/skills" "$CLAUDE_DIR/skills"
echo "  Linked skills/"

echo ""
echo "Done! Restart Claude Code for changes to take effect."
echo ""
echo "Note: settings.local.json is intentionally NOT linked (machine-specific permissions)."
