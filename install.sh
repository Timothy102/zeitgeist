#!/bin/bash

SKILL_NAME="zeitgeist"
SKILL_DIR="$HOME/.claude/skills/$SKILL_NAME"

echo "Installing $SKILL_NAME skill for Claude Code..."

# Create skills directory if it doesn't exist
mkdir -p "$HOME/.claude/skills"

# Remove existing installation if present
if [ -d "$SKILL_DIR" ]; then
    echo "Removing existing installation..."
    rm -rf "$SKILL_DIR"
fi

# Get the directory where install.sh is located
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Copy skill files to Claude skills directory
cp -r "$SCRIPT_DIR" "$SKILL_DIR"

# Remove .git and install.sh from installed copy
rm -rf "$SKILL_DIR/.git"
rm -f "$SKILL_DIR/install.sh"

echo ""
echo "✓ Installed to $SKILL_DIR"
echo ""
echo "Usage: /zeitgeist [niche, vertical, or audience]"
echo ""
echo "Examples:"
echo "  /zeitgeist sneaker culture"
echo "  /zeitgeist millennial parents"
echo "  /zeitgeist indie beauty brands"
