#!/bin/bash
# Diagnose whether token-optimizer plugin artifacts are causing
# Claude Code to hang. This script is read-only and makes no changes.
#
# Usage: bash diagnose.sh
#
# Exit codes:
#   0 = no issues found
#   1 = token-optimizer artifacts detected

set -euo pipefail

CLAUDE_DIR="${HOME}/.claude"
SETTINGS_FILE="${CLAUDE_DIR}/settings.json"
SKILL_LINK="${CLAUDE_DIR}/skills/token-optimizer"
INSTALL_DIR="${CLAUDE_DIR}/token-optimizer"
BACKUPS_DIR="${CLAUDE_DIR}/_backups/token-optimizer"

issues_found=0

echo "=== Token-Optimizer Diagnostic ==="
echo ""

# Check 1: settings.json hooks
echo "[1/3] Checking settings.json for token-optimizer hooks..."
if [ -f "$SETTINGS_FILE" ]; then
    hook_count=$(grep -c "token-optimizer" "$SETTINGS_FILE" 2>/dev/null || true)
    compaction_count=$(grep -c "COMPACTION GUIDANCE" "$SETTINGS_FILE" 2>/dev/null || true)
    total=$((hook_count + compaction_count))

    if [ "$total" -gt 0 ]; then
        echo "  FOUND: $total token-optimizer hook reference(s) in settings.json"
        issues_found=1
    else
        echo "  OK: No token-optimizer hooks in settings.json"
    fi
else
    echo "  OK: No settings.json file found (nothing to clean)"
fi

# Check 2: symlink
echo ""
echo "[2/3] Checking for token-optimizer symlink..."
if [ -L "$SKILL_LINK" ]; then
    target=$(readlink "$SKILL_LINK" 2>/dev/null || echo "unknown")
    if [ -d "$SKILL_LINK" ]; then
        echo "  FOUND: Symlink exists at $SKILL_LINK -> $target"
    else
        echo "  FOUND: Broken symlink at $SKILL_LINK -> $target"
    fi
    issues_found=1
elif [ -d "$SKILL_LINK" ]; then
    echo "  FOUND: Directory exists at $SKILL_LINK (not a symlink)"
    issues_found=1
else
    echo "  OK: No symlink found"
fi

# Check 3: leftover data directories
echo ""
echo "[3/3] Checking for leftover data directories..."
leftover=0
if [ -d "$INSTALL_DIR" ]; then
    echo "  FOUND: Installation directory at $INSTALL_DIR"
    leftover=1
fi
if [ -d "$BACKUPS_DIR" ]; then
    echo "  FOUND: Backup data at $BACKUPS_DIR"
    leftover=1
fi
if [ "$leftover" -eq 0 ]; then
    echo "  OK: No leftover directories found"
else
    issues_found=1
fi

# Summary
echo ""
echo "=================================="
if [ "$issues_found" -eq 1 ]; then
    echo "RESULT: Token-optimizer artifacts detected."
    echo ""
    echo "To fix, run:  bash fix-claude-stuck.sh"
    exit 1
else
    echo "RESULT: No issues found. Your Claude Code installation looks clean."
    exit 0
fi
