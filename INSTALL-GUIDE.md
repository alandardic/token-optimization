# Safe Installation Guide for Token-Optimizer

This guide walks you through safely installing the
[token-optimizer](https://github.com/alexgreensh/token-optimizer) plugin
for Claude Code, with proper safeguards so you can cleanly uninstall it
if anything goes wrong.

---

## Before You Start

Make sure you have these installed on your machine:

- **Python 3.8+** — run `python3 --version` to check
- **Git** — run `git --version` to check
- **Claude Code** — the desktop app should be installed and working

---

## Step 1: Back Up Your Current Settings

This is the most important step. Open a regular terminal and run:

```bash
cp ~/.claude/settings.json ~/.claude/settings.json.pre-token-optimizer
```

If the file doesn't exist yet, that's fine — skip this step.

This backup lets you instantly restore Claude Code to its current working
state if anything goes wrong:

```bash
cp ~/.claude/settings.json.pre-token-optimizer ~/.claude/settings.json
```

---

## Step 2: Install the Plugin Using the Official Script

Run the installer from your terminal (not from inside Claude Code):

```bash
curl -fsSL https://raw.githubusercontent.com/alexgreensh/token-optimizer/main/install.sh | bash
```

Or if you prefer to inspect the script first (recommended):

```bash
curl -fsSL https://raw.githubusercontent.com/alexgreensh/token-optimizer/main/install.sh -o install-token-optimizer.sh
cat install-token-optimizer.sh   # Read it, make sure you're comfortable
bash install-token-optimizer.sh
```

The installer will:
- Clone the repo to `~/.claude/token-optimizer/`
- Create a symlink at `~/.claude/skills/token-optimizer`
- Add hooks to `~/.claude/settings.json`
- Set up the quality measurement bar

---

## Step 3: Verify the Installation

After installing, check that the key files exist:

```bash
# The plugin directory should exist
ls ~/.claude/token-optimizer/

# The symlink should point to the skills directory
ls -la ~/.claude/skills/token-optimizer

# Settings should now contain token-optimizer hooks
grep -c "token-optimizer" ~/.claude/settings.json
```

You should see a count of 10+ hook references in settings.json.

---

## Step 4: Test Claude Code

1. Open Claude Code (or restart it if already open)
2. Try a simple action — ask it to read a file or answer a question
3. If Claude Code works normally, the installation succeeded
4. If Claude Code hangs or gets stuck, go to the Emergency Recovery
   section below

---

## Step 5: Using the Plugin

Once installed, the plugin works automatically in the background. It:
- Tracks token usage per turn
- Provides quality scoring for your context window
- Optimizes compaction behavior
- Offers a dashboard at `http://localhost:24842/token-optimizer`

You can use the `/token-optimizer` skill command inside Claude Code to
run audits and see optimization recommendations.

---

## How to Properly Uninstall

**NEVER just delete the plugin folder.** That's what caused the original
problem. Instead, follow these steps:

### Option A: Use the cleanup scripts from this repo

```bash
git clone https://github.com/alandardic/token-optimization.git
cd token-optimization
bash fix-claude-stuck.sh --yes
```

### Option B: Manual uninstall

```bash
# 1. Remove hooks from settings.json
#    Open ~/.claude/settings.json and delete all entries
#    where "command" contains "token-optimizer"

# 2. Remove the symlink
rm -f ~/.claude/skills/token-optimizer

# 3. Remove the plugin directory
rm -rf ~/.claude/token-optimizer

# 4. Remove plugin data
rm -rf ~/.claude/_backups/token-optimizer
```

### Option C: Restore your backup

If you made the backup in Step 1:

```bash
cp ~/.claude/settings.json.pre-token-optimizer ~/.claude/settings.json
rm -f ~/.claude/skills/token-optimizer
rm -rf ~/.claude/token-optimizer
rm -rf ~/.claude/_backups/token-optimizer
```

After any uninstall method, restart Claude Code.

---

## Emergency Recovery

If Claude Code gets stuck after installation:

1. **Don't panic** — your files and projects are fine
2. Open a regular terminal (not Claude Code)
3. Restore your settings backup:
   ```bash
   cp ~/.claude/settings.json.pre-token-optimizer ~/.claude/settings.json
   ```
4. If you didn't make a backup, use the fix script:
   ```bash
   git clone https://github.com/alandardic/token-optimization.git
   cd token-optimization
   bash fix-claude-stuck.sh --yes
   ```
5. Restart Claude Code

---

## Key Safety Rules

1. **Always back up settings.json before installing any plugin**
2. **Never delete a plugin folder without removing its hooks first**
3. **Install from a terminal, not from inside Claude Code** — if the
   install fails mid-way, Claude Code won't be affected
4. **Keep this repo bookmarked** as your emergency recovery tool
