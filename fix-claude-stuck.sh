#!/bin/bash
# Fix Claude Code hanging after token-optimizer plugin removal.
#
# This script removes leftover token-optimizer hooks from
# ~/.claude/settings.json and cleans up related artifacts.
# It preserves all non-token-optimizer settings and hooks.
#
# Usage:
#   bash fix-claude-stuck.sh            # Interactive (prompts for confirmation)
#   bash fix-claude-stuck.sh --yes      # Skip confirmation
#   bash fix-claude-stuck.sh --dry-run  # Show what would be done

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Parse arguments
DRY_RUN=""
AUTO_YES=""
for arg in "$@"; do
    case "$arg" in
        --dry-run) DRY_RUN="--dry-run" ;;
        --yes|-y) AUTO_YES="true" ;;
        --help|-h)
            echo "Usage: bash fix-claude-stuck.sh [--yes] [--dry-run]"
            echo ""
            echo "Removes token-optimizer plugin artifacts that cause Claude Code to hang."
            echo ""
            echo "Options:"
            echo "  --yes, -y    Skip confirmation prompt"
            echo "  --dry-run    Show what would be done without making changes"
            echo "  --help, -h   Show this help message"
            exit 0
            ;;
    esac
done

echo "=== Token-Optimizer Cleanup ==="
echo ""

# Check Python 3 is available
if ! command -v python3 &>/dev/null; then
    echo "ERROR: python3 is required but not found."
    echo ""
    echo "Please install Python 3.8+ and try again, or manually edit"
    echo "~/.claude/settings.json to remove hooks containing 'token-optimizer'."
    exit 1
fi

# Check ~/.claude directory exists
if [ ! -d "${HOME}/.claude" ]; then
    echo "No ~/.claude directory found. Nothing to clean up."
    exit 0
fi

# Run diagnosis first
echo "Running diagnosis..."
echo ""
bash "${SCRIPT_DIR}/diagnose.sh" || true
echo ""

# Confirm unless --yes or --dry-run
if [ -z "$AUTO_YES" ] && [ -z "$DRY_RUN" ]; then
    echo "This will remove all token-optimizer hooks and artifacts listed above."
    echo "A backup of settings.json will be created before any changes."
    echo ""
    read -r -p "Proceed? [y/N] " response
    case "$response" in
        [yY]|[yY][eE][sS]) ;;
        *)
            echo "Aborted."
            exit 0
            ;;
    esac
    echo ""
fi

# Run the Python cleanup
python3 "${SCRIPT_DIR}/fix.py" $DRY_RUN

echo ""
if [ -z "$DRY_RUN" ]; then
    echo "Done! Please restart Claude Code for the fix to take effect."
fi
