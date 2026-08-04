#!/usr/bin/env bash
# install.sh — Install skills from ecrespo/skills into any agent's skills directory.
#
# Works from a local clone or standalone (downloads the repo tarball).
#
# Usage:
#   ./scripts/install.sh [options]
#   curl -fsSL https://raw.githubusercontent.com/ecrespo/skills/main/scripts/install.sh | bash -s -- [options]
#
# Options:
#   --target claude-user     Install to ~/.claude/skills (Claude Code, all projects) [default]
#   --target claude-project  Install to ./.claude/skills (Claude Code, current repo)
#   --target opencode        Install to ~/.config/opencode/skills
#   --dest DIR               Install to an arbitrary skills directory (any agent)
#   --skills a,b,c           Comma-separated skill names (default: all)
#   --list                   List available skills and exit
#   --ref REF                Git ref to download when not run from a clone (default: main)
#   --dry-run                Show what would be copied without copying
#
# Claude Desktop cannot be installed via the filesystem: download the .skill
# bundles from https://github.com/ecrespo/skills/releases and add them in
# Settings > Capabilities > Skills.
set -euo pipefail

REPO="ecrespo/skills"
REF="main"
TARGET="claude-user"
DEST=""
ONLY=""
DRY_RUN=0
LIST=0

while [ $# -gt 0 ]; do
  case "$1" in
    --target)  TARGET="$2"; shift 2 ;;
    --dest)    DEST="$2"; TARGET="custom"; shift 2 ;;
    --skills)  ONLY="$2"; shift 2 ;;
    --ref)     REF="$2"; shift 2 ;;
    --list)    LIST=1; shift ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help) sed -n '2,24p' "$0" 2>/dev/null || true; exit 0 ;;
    *) echo "Unknown option: $1" >&2; exit 2 ;;
  esac
done

# Locate the skills/ source: local clone (script lives in scripts/) or download.
CLEANUP=""
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-.}")" 2>/dev/null && pwd || true)"
if [ -n "$SCRIPT_DIR" ] && [ -d "$SCRIPT_DIR/../skills" ]; then
  SRC="$(cd "$SCRIPT_DIR/.." && pwd)/skills"
else
  TMP="$(mktemp -d)"
  CLEANUP="$TMP"
  echo "Downloading $REPO@$REF ..."
  curl -fsSL "https://github.com/$REPO/archive/refs/heads/$REF.tar.gz" | tar -xz -C "$TMP"
  SRC="$(find "$TMP" -maxdepth 2 -type d -name skills | head -1)"
  [ -n "$SRC" ] || { echo "ERROR: skills/ not found in downloaded archive" >&2; exit 1; }
fi
trap '[ -n "$CLEANUP" ] && rm -rf "$CLEANUP"' EXIT

if [ "$LIST" = 1 ]; then
  echo "Available skills:"
  for d in "$SRC"/*/; do
    [ -f "$d/SKILL.md" ] && echo "  - $(basename "$d")"
  done
  exit 0
fi

case "$TARGET" in
  claude-user)    DEST="$HOME/.claude/skills" ;;
  claude-project) DEST="$(pwd)/.claude/skills" ;;
  opencode)       DEST="${XDG_CONFIG_HOME:-$HOME/.config}/opencode/skills" ;;
  custom)         [ -n "$DEST" ] || { echo "ERROR: --dest required" >&2; exit 2; } ;;
  *) echo "ERROR: unknown target '$TARGET'" >&2; exit 2 ;;
esac

install_one() {
  name="$1"
  src="$SRC/$name"
  [ -f "$src/SKILL.md" ] || { echo "SKIP $name (no SKILL.md)"; return; }
  if [ "$DRY_RUN" = 1 ]; then
    echo "DRY  $name -> $DEST/$name"
    return
  fi
  mkdir -p "$DEST"
  rm -rf "${DEST:?}/$name"
  cp -R "$src" "$DEST/$name"
  find "$DEST/$name" -name __pycache__ -type d -exec rm -rf {} + 2>/dev/null || true
  echo "OK   $name -> $DEST/$name"
}

if [ -n "$ONLY" ]; then
  IFS=',' read -ra NAMES <<< "$ONLY"
  for n in "${NAMES[@]}"; do install_one "$(echo "$n" | tr -d ' ')"; done
else
  for d in "$SRC"/*/; do install_one "$(basename "$d")"; done
fi

[ "$DRY_RUN" = 1 ] || echo "Done. Skills installed in $DEST"
