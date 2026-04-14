#!/usr/bin/env python3
"""Remove token-optimizer plugin hooks and artifacts from Claude Code.

The token-optimizer plugin (https://github.com/alexgreensh/token-optimizer)
installs lifecycle hooks into ~/.claude/settings.json. If the plugin files
are deleted without a proper uninstall, these hooks remain and point to
non-existent scripts, causing Claude Code to hang on every operation.

This script removes those hooks while preserving all other settings.

Usage:
    python3 fix.py              # Run the cleanup
    python3 fix.py --dry-run    # Show what would be done without changing anything
    python3 fix.py --settings-path /path/to/settings.json  # Use a custom path
"""

import argparse
import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path


def is_token_optimizer_hook(entry):
    """Check if a hook entry belongs to the token-optimizer plugin."""
    for hook in entry.get("hooks", []):
        cmd = hook.get("command", "")
        if "token-optimizer" in cmd:
            return True
        # The plugin also installs a compaction guidance echo
        if cmd.startswith("echo COMPACTION GUIDANCE:"):
            return True
    return False


def clean_settings(settings_path, dry_run=False):
    """Remove token-optimizer hooks from settings.json.

    Returns (hooks_removed_count, hooks_preserved_count).
    """
    if not settings_path.exists():
        print(f"  No settings file found at {settings_path}")
        return 0, 0

    with open(settings_path, "r", encoding="utf-8") as f:
        try:
            settings = json.load(f)
        except json.JSONDecodeError as e:
            print(f"  ERROR: Failed to parse {settings_path}: {e}")
            print("  Please fix the JSON manually or restore from backup.")
            sys.exit(1)

    hooks = settings.get("hooks", {})
    if not hooks:
        print("  No hooks found in settings.json")
        return 0, 0

    total_removed = 0
    total_preserved = 0
    events_to_delete = []

    for event_name, entries in hooks.items():
        if not isinstance(entries, list):
            continue

        kept = []
        removed = 0
        for entry in entries:
            if is_token_optimizer_hook(entry):
                removed += 1
                cmd_preview = ""
                for h in entry.get("hooks", []):
                    cmd_preview = h.get("command", "")[:80]
                    break
                print(f"  Removing [{event_name}]: {cmd_preview}...")
            else:
                kept.append(entry)

        total_removed += removed
        total_preserved += len(kept)

        if kept:
            hooks[event_name] = kept
        else:
            events_to_delete.append(event_name)

    for event_name in events_to_delete:
        del hooks[event_name]

    if not hooks:
        del settings["hooks"]

    if total_removed == 0:
        print("  No token-optimizer hooks found in settings.json")
        return 0, total_preserved

    if dry_run:
        print(f"\n  DRY RUN: Would remove {total_removed} hook(s), "
              f"preserve {total_preserved} hook(s)")
        return total_removed, total_preserved

    # Back up before modifying
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_path = settings_path.parent / f"settings.json.backup-{timestamp}"
    shutil.copy2(settings_path, backup_path)
    print(f"  Backup saved to: {backup_path}")

    with open(settings_path, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=4)
        f.write("\n")

    print(f"  Removed {total_removed} token-optimizer hook(s)")
    print(f"  Preserved {total_preserved} other hook(s)")
    return total_removed, total_preserved


def clean_symlink(skills_dir, dry_run=False):
    """Remove the token-optimizer symlink from skills directory."""
    link_path = skills_dir / "token-optimizer"

    if not link_path.exists() and not link_path.is_symlink():
        print("  No symlink found at", link_path)
        return False

    if link_path.is_symlink():
        target = os.readlink(link_path)
        if dry_run:
            print(f"  DRY RUN: Would remove symlink {link_path} -> {target}")
        else:
            link_path.unlink()
            print(f"  Removed symlink: {link_path} -> {target}")
        return True

    if link_path.is_dir():
        print(f"  WARNING: {link_path} is a real directory, not a symlink.")
        print("  Skipping removal — please inspect manually.")
        return False

    return False


def clean_data_dirs(claude_dir, dry_run=False):
    """Remove leftover token-optimizer data directories."""
    dirs_to_check = [
        claude_dir / "token-optimizer",
        claude_dir / "_backups" / "token-optimizer",
    ]

    removed = []
    for dir_path in dirs_to_check:
        if dir_path.exists():
            if dry_run:
                print(f"  DRY RUN: Would remove directory {dir_path}")
            else:
                shutil.rmtree(dir_path)
                print(f"  Removed directory: {dir_path}")
            removed.append(dir_path)

    if not removed:
        print("  No leftover data directories found")

    return removed


def main():
    parser = argparse.ArgumentParser(
        description="Remove token-optimizer plugin artifacts from Claude Code"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    parser.add_argument(
        "--settings-path",
        type=Path,
        default=None,
        help="Path to settings.json (default: ~/.claude/settings.json)",
    )
    args = parser.parse_args()

    claude_dir = Path.home() / ".claude"
    settings_path = args.settings_path or (claude_dir / "settings.json")

    if args.dry_run:
        print("=== DRY RUN MODE — no changes will be made ===\n")

    # Step 1: Clean hooks from settings.json
    print("[1/3] Cleaning token-optimizer hooks from settings.json...")
    hooks_removed, hooks_preserved = clean_settings(settings_path, args.dry_run)

    # Step 2: Remove symlink
    print("\n[2/3] Checking for token-optimizer symlink...")
    skills_dir = claude_dir / "skills"
    clean_symlink(skills_dir, args.dry_run)

    # Step 3: Remove data directories
    print("\n[3/3] Checking for leftover data directories...")
    clean_data_dirs(claude_dir, args.dry_run)

    # Summary
    print("\n" + "=" * 50)
    if args.dry_run:
        print("DRY RUN complete. No changes were made.")
        print("Run without --dry-run to apply the fix.")
    elif hooks_removed > 0:
        print("Cleanup complete! Restart Claude Code for changes to take effect.")
    else:
        print("No token-optimizer artifacts found. Your installation looks clean.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
