# Fix: Claude Code Stuck After Token-Optimizer Removal

## Problem

After installing the [token-optimizer](https://github.com/alexgreensh/token-optimizer) plugin and then deleting its files, Claude Code becomes stuck and unable to perform any operations.

**Why this happens**: The plugin's installer adds lifecycle hooks to `~/.claude/settings.json` that fire on nearly every Claude Code operation (reading files, running commands, starting/stopping sessions, compacting context, etc.). When the plugin folder is deleted without a proper uninstall, these hooks remain in `settings.json` and point to scripts that no longer exist, causing Claude Code to hang.

## Quick Fix

1. Clone this repo or download the scripts
2. Run the fix:

```bash
bash fix-claude-stuck.sh
```

3. Restart Claude Code

## Diagnosis Only

To check if you're affected without making changes:

```bash
bash diagnose.sh
```

## What Gets Removed

- **Hooks in `~/.claude/settings.json`**: All hook entries whose commands reference `token-optimizer` scripts (across 11 lifecycle events: PreToolUse, PostToolUse, SessionStart, Stop, SessionEnd, PreCompact, PostCompact, UserPromptSubmit, CwdChanged, StopFailure)
- **Symlink**: `~/.claude/skills/token-optimizer`
- **Data directories**: `~/.claude/token-optimizer/` and `~/.claude/_backups/token-optimizer/`

## What Gets Preserved

- All non-token-optimizer hooks (e.g., your own custom hooks)
- All other settings (permissions, `$schema`, etc.)
- A timestamped backup of `settings.json` is created before any changes

## Options

```
bash fix-claude-stuck.sh --dry-run    # Preview changes without applying
bash fix-claude-stuck.sh --yes        # Skip confirmation prompt
python3 fix.py --dry-run              # Run the Python cleanup directly
```

## Manual Fix

If you prefer to fix it manually, open `~/.claude/settings.json` in a text editor and remove all hook entries where the `command` contains `token-optimizer`. If a hook event category (e.g., `PreToolUse`) becomes empty after removing entries, delete the entire category. If the `hooks` object becomes empty, remove it.
