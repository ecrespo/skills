# Installing these skills in Claude Code

Claude Code discovers skills from three places, in this order of specificity:

| Scope | Location | Applies to |
|---|---|---|
| Project | `.claude/skills/<name>/` inside a repo | That repo only; commit it to share with the team |
| User | `~/.claude/skills/<name>/` | Every project on the machine |
| Plugin | installed through a plugin marketplace | Every project, managed and updatable as a bundle |

A skill is just a folder with a `SKILL.md` inside one of those directories. Pick one method below.

## Method 1 — Plugin marketplace (recommended)

Installs all seven skills as one managed bundle that updates together.

```
/plugin marketplace add ecrespo/skills
/plugin install ecrespo-skills@ecrespo-skills
```

Run both inside a Claude Code session. To pick up later changes:

```
/plugin marketplace update ecrespo-skills
```

Use this when you want the collection as-is. If you plan to edit the skills, use method 2 or 3
instead — plugin files are managed and get overwritten on update.

## Method 2 — skills.sh installer

Copies the skills into your project as ordinary files you own and can edit.

```bash
npx skills@latest add ecrespo/skills
```

It detects the agents on your machine, asks which skills to copy, and writes them into the
project. Add `--global` to install into `~/.claude/skills` instead, or `-s infografia-animada`
to take just one skill.

## Method 3 — Bundled installer (no Node required)

From a clone:

```bash
git clone https://github.com/ecrespo/skills.git
cd skills
./scripts/install.sh                          # all skills -> ~/.claude/skills
./scripts/install.sh --target claude-project  # -> ./.claude/skills of the current repo
./scripts/install.sh --skills infografia-animada
```

Without cloning:

```bash
curl -fsSL https://raw.githubusercontent.com/ecrespo/skills/main/scripts/install.sh | bash -s -- --skills infografia-animada
```

`--list` shows what is available, `--dry-run` previews the copy, `--dest DIR` targets any other
skills directory.

## Method 4 — Manual copy

```bash
git clone https://github.com/ecrespo/skills.git ~/src/skills
mkdir -p ~/.claude/skills
cp -r ~/src/skills/skills/infografia-animada ~/.claude/skills/
```

Symlinking instead of copying (`ln -s ~/src/skills/skills/infografia-animada ~/.claude/skills/`)
keeps the skill in sync with `git pull`, which is handy while iterating on a skill you are editing.

## Verifying the installation

1. Start a new Claude Code session, or run `/context` in the current one. Skills are read at
   session start, so an install mid-session is not visible until the session restarts.
2. Ask for the skill by name with a slash command: `/infografia-animada`. If Claude loads it, the
   frontmatter parsed correctly.
3. Confirm the files landed where you expect:

   ```bash
   ls ~/.claude/skills/infografia-animada
   # SKILL.md  assets  references  scripts
   ```

4. Smoke-test the bundled scripts:

   ```bash
   python3 ~/.claude/skills/infografia-animada/scripts/setup_project.py --help
   python3 ~/.claude/skills/infografia-animada/scripts/to_gif.py --help
   ```

If a skill never triggers on its own, the description is the only signal Claude sees when deciding
whether to load it. Naming the skill explicitly (`/name`, or "use the X skill") always works.

## Prerequisites per skill

Six of the seven skills need nothing beyond Python 3, which their scripts use from the standard
library. `infografia-animada` drives external tools:

```bash
node --version    # 18 or newer, ships npx
ffmpeg -version   # needed only for the MP4 -> GIF step
```

On Debian or Ubuntu: `sudo apt install ffmpeg`. On macOS: `brew install ffmpeg`. Node.js comes from
[nodejs.org](https://nodejs.org) or a version manager such as nvm. Remotion itself is installed
per project by `scripts/setup_project.py`, not globally, and downloads a headless Chrome build the
first time it renders.

## Updating

| Installed with | Update command |
|---|---|
| Plugin marketplace | `/plugin marketplace update ecrespo-skills` |
| skills.sh | `npx skills@latest update` |
| install.sh | re-run the same command; it overwrites the skill folders |
| Manual copy | `git pull` in the clone, then copy again (or symlink once, see method 4) |

## Uninstalling

```
/plugin uninstall ecrespo-skills@ecrespo-skills
```

For file-based installs, delete the folder:

```bash
rm -rf ~/.claude/skills/infografia-animada
```

## Troubleshooting

- **The skill does not appear.** Restart the session. Check that the folder name matches the `name`
  in the frontmatter, and that `SKILL.md` opens with a `---` frontmatter block.
- **The skill loads but a reference file is missing.** Copy the whole skill folder, not just
  `SKILL.md`: the `references/`, `scripts/` and `assets/` subfolders are part of it. Run
  `python3 scripts/validate_and_package.py --no-package` from a clone to confirm every referenced
  path exists.
- **Two skills compete for the same task.** The more specific description wins. `infografia-animada`
  states that it takes precedence over generic Remotion or video skills when the result is an
  animated infographic; name the skill explicitly to settle it.
- **`setup_project.py` fails on npx.** Node is missing or not on PATH. The script checks and reports
  this before touching the filesystem.
